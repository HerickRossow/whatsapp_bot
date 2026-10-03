import json

from src.application.services.AgenteAtendimentoService import AgenteAtendimentoService
from src.domain.entities.Produto import Produto
from src.domain.value_objects.ChamadaFerramenta import ChamadaFerramenta
from src.domain.value_objects.Dinheiro import Dinheiro
from src.domain.value_objects.RespostaAssistente import RespostaAssistente
from src.infra.Container import Container

from ...fakes import AssistenteIAGatewayFake, WhatsAppGatewayFake


def _montar_container_com_roteiro(database, settings_teste, roteiro):
    gateway = AssistenteIAGatewayFake(roteiro)
    container = Container(
        settings_teste, database=database,
        whatsapp_gateway=WhatsAppGatewayFake(), assistente_gateway=gateway,
    )
    return container, gateway


def test_tool_call_seguida_de_resposta_final(database, settings_teste):
    roteiro = [
        RespostaAssistente(mensagens=[], chamadas_ferramenta=[
            ChamadaFerramenta("tool_1", "buscar_produtos", {"consulta": "creatina"})
        ]),
        RespostaAssistente(mensagens=[], texto_final="Temos Creatina por R$ 79,90!"),
    ]
    container, gateway = _montar_container_com_roteiro(database, settings_teste, roteiro)
    container.produto_repository.salvar(Produto(nome="Creatina", preco=Dinheiro("79.90"), estoque=10, sku="CR001"))

    cliente = container.obter_ou_criar_cliente_usecase.executar("11988887777", "Joao")
    resposta = container.agente_atendimento_service.processar_mensagem(cliente, "Tem creatina?")

    assert "Creatina" in resposta
    segunda_chamada_mensagens = gateway.chamadas_recebidas[1][1]
    resultado_tool = json.loads(segunda_chamada_mensagens[-1]["content"][0]["content"])
    assert resultado_tool["encontrados"] == 1


def test_erro_de_dominio_e_traduzido_para_o_formato_esperado(database, settings_teste):
    roteiro = [
        RespostaAssistente(mensagens=[], chamadas_ferramenta=[
            ChamadaFerramenta("tool_1", "adicionar_carrinho", {"produto_id": "id-invalido", "quantidade": 1})
        ]),
        RespostaAssistente(mensagens=[], texto_final="Não encontrei esse produto."),
    ]
    container, gateway = _montar_container_com_roteiro(database, settings_teste, roteiro)

    cliente = container.obter_ou_criar_cliente_usecase.executar("11988887777", "Joao")
    container.agente_atendimento_service.processar_mensagem(cliente, "Quero o produto X")

    mensagens = gateway.chamadas_recebidas[1][1]
    resultado_tool = json.loads(mensagens[-1]["content"][0]["content"])
    assert resultado_tool == {"erro": "produto_nao_encontrado"}


def test_limite_de_turnos_e_respeitado_quando_modelo_nunca_finaliza(database, settings_teste):
    roteiro = [
        RespostaAssistente(mensagens=[], chamadas_ferramenta=[ChamadaFerramenta("t", "consultar_frete", {})])
        for _ in range(10)
    ]
    container, gateway = _montar_container_com_roteiro(database, settings_teste, roteiro)

    cliente = container.obter_ou_criar_cliente_usecase.executar("11988887777", "Joao")
    resposta = container.agente_atendimento_service.processar_mensagem(cliente, "oi")

    assert "tive um problema" in resposta
    assert len(gateway.chamadas_recebidas) == AgenteAtendimentoService.LIMITE_TURNOS
