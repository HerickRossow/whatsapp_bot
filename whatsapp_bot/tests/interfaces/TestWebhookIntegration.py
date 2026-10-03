import openpyxl
from fastapi.testclient import TestClient

from src.domain.entities.Administrador import Administrador
from src.domain.value_objects.Telefone import Telefone
from src.interfaces.api.Main import app


def _cliente(container):
    app.state.container = container
    return TestClient(app)


def test_health(container):
    cliente = _cliente(container)
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_webhook_verificacao_com_token_correto(container):
    cliente = _cliente(container)
    resposta = cliente.get("/webhook", params={
        "hub.mode": "subscribe", "hub.verify_token": "token123", "hub.challenge": "abc123",
    })
    assert resposta.status_code == 200
    assert resposta.text == "abc123"


def test_webhook_verificacao_com_token_errado(container):
    cliente = _cliente(container)
    resposta = cliente.get("/webhook", params={
        "hub.mode": "subscribe", "hub.verify_token": "errado", "hub.challenge": "abc123",
    })
    assert resposta.status_code == 403


def test_webhook_mensagem_de_texto_cria_cliente_e_responde(container, whatsapp_gateway_fake):
    cliente_http = _cliente(container)
    payload = {
        "entry": [{"changes": [{"value": {
            "contacts": [{"wa_id": "11988887777", "profile": {"name": "Joao"}}],
            "messages": [{"from": "11988887777", "type": "text", "id": "msg1", "timestamp": "123",
                          "text": {"body": "Oi"}}],
        }}]}]
    }
    resposta = cliente_http.post("/webhook", json=payload)
    assert resposta.status_code == 200

    cliente_criado = container.cliente_repository.buscar_por_whatsapp(Telefone("11988887777"))
    assert cliente_criado is not None and cliente_criado.nome == "Joao"
    assert len(container.conversa_repository.buscar_historico(cliente_criado.id)) == 2
    assert whatsapp_gateway_fake.mensagens


def test_webhook_comando_admin_pedido_inexistente(container, whatsapp_gateway_fake):
    container.administrador_repository.salvar(Administrador(whatsapp=Telefone("11999998888"), nome="Admin"))
    cliente_http = _cliente(container)
    payload = {
        "entry": [{"changes": [{"value": {
            "contacts": [{"wa_id": "11999998888", "profile": {"name": "Admin"}}],
            "messages": [{"from": "11999998888", "type": "text", "id": "msg2", "timestamp": "124",
                          "text": {"body": "STATUS 000001"}}],
        }}]}]
    }
    resposta = cliente_http.post("/webhook", json=payload)
    assert resposta.status_code == 200
    assert any("Não encontrei o pedido" in m for tel, m in whatsapp_gateway_fake.mensagens if tel == "11999998888")


def test_sync_produtos_sucesso_e_arquivo_ausente(container, settings_teste):
    cliente_http = _cliente(container)

    resposta_sem_arquivo = cliente_http.post("/sync-produtos")
    assert resposta_sem_arquivo.status_code == 400

    workbook = openpyxl.Workbook()
    planilha = workbook.active
    planilha.append(["ID", "SKU", "Produto", "Marca", "Categoria", "Peso", "Sabor", "Preço", "Estoque",
                      "Descricao", "Imagem", "Ativo"])
    planilha.append([1, "CR001", "Creatina", "Growth", "Creatina", "250g", "-", "79,90", 10,
                      "Creatina monoidratada", "creatina.jpg", "SIM"])
    settings_teste.produtos_xlsx.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(settings_teste.produtos_xlsx)

    resposta_ok = cliente_http.post("/sync-produtos")
    assert resposta_ok.status_code == 200
    assert resposta_ok.json()["produtos_sincronizados"] == 1
