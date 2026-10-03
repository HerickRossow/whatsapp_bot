import logging

from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse

from ....domain.entities.Conversa import Conversa
from ....domain.value_objects.Telefone import Telefone
from ....infra.external.WebhookPayloadParser import parse_incoming, verificar_token
from ..AdminComandoHandler import tratar_comando_admin

logger = logging.getLogger("webhook")
router = APIRouter()


@router.get("/webhook")
def verificar_webhook(request: Request,
                       hub_mode: str = Query(default=None, alias="hub.mode"),
                       hub_verify_token: str = Query(default=None, alias="hub.verify_token"),
                       hub_challenge: str = Query(default=None, alias="hub.challenge")):
    container = request.app.state.container
    resultado = verificar_token(hub_mode, hub_verify_token, hub_challenge, container.settings.whatsapp_verify_token)
    if resultado is not None:
        return PlainTextResponse(resultado)
    return PlainTextResponse("forbidden", status_code=403)


@router.post("/webhook")
async def receber_webhook(request: Request):
    container = request.app.state.container
    payload = await request.json()
    mensagens = parse_incoming(payload)

    for mensagem in mensagens:
        try:
            _processar_uma_mensagem(container, mensagem)
        except Exception as erro:
            logger.exception("Erro processando mensagem %s", mensagem.get("message_id"))
            _notificar_admin_sobre_erro(container, mensagem, erro)

    return {"status": "received"}


def _notificar_admin_sobre_erro(container, mensagem: dict, erro: Exception) -> None:
    if not container.settings.admin_whatsapp:
        return
    try:
        container.whatsapp_gateway.enviar_texto(
            Telefone(container.settings.admin_whatsapp),
            f"🚨 ERRO NO BOT\n\nMensagem: {mensagem.get('message_id')}\nErro: {erro}",
        )
    except Exception:
        logger.exception("Falha ao notificar admin sobre erro de processamento")


def _processar_uma_mensagem(container, mensagem: dict) -> None:
    telefone_texto = mensagem.get("telefone")
    if not telefone_texto:
        return

    telefone = Telefone(telefone_texto)

    if container.administrador_repository.eh_admin(telefone) and mensagem["tipo"] == "text":
        resposta_admin = tratar_comando_admin(container, mensagem.get("texto"))
        if resposta_admin is not None:
            container.whatsapp_gateway.enviar_texto(telefone, resposta_admin)
            return

    cliente = container.obter_ou_criar_cliente_usecase.executar(telefone_texto, mensagem.get("nome"))

    if mensagem["tipo"] == "text" and mensagem.get("texto"):
        _responder_mensagem_de_texto(container, cliente, mensagem["texto"], telefone)
    elif mensagem["tipo"] == "image":
        _responder_comprovante(container, cliente, mensagem, telefone)
    else:
        container.whatsapp_gateway.enviar_texto(
            telefone, "Recebi sua mensagem, mas por enquanto só consigo processar texto e imagens de comprovante. 🙂"
        )


def _responder_mensagem_de_texto(container, cliente, texto: str, telefone: Telefone) -> None:
    container.conversa_repository.salvar(
        Conversa(cliente_id=cliente.id, tipo="texto", mensagem=texto, origem="cliente")
    )
    resposta = container.agente_atendimento_service.processar_mensagem(cliente, texto)
    container.conversa_repository.salvar(
        Conversa(cliente_id=cliente.id, tipo="texto", mensagem=resposta, origem="bot")
    )
    container.whatsapp_gateway.enviar_texto(telefone, resposta)


def _responder_comprovante(container, cliente, mensagem: dict, telefone: Telefone) -> None:
    container.conversa_repository.salvar(
        Conversa(
            cliente_id=cliente.id, tipo="imagem",
            mensagem=mensagem.get("texto") or "[imagem recebida]", origem="cliente",
        )
    )
    resposta = container.processar_comprovante_usecase.executar(
        cliente, mensagem["media_id"], mensagem.get("mime_type")
    )
    container.conversa_repository.salvar(
        Conversa(cliente_id=cliente.id, tipo="texto", mensagem=resposta, origem="bot")
    )
    container.whatsapp_gateway.enviar_texto(telefone, resposta)
