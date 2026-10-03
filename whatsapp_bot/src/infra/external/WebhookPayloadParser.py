import logging
from typing import Optional

logger = logging.getLogger("webhook_parser")


def verificar_token(modo: Optional[str], token: Optional[str], challenge: Optional[str],
                     token_esperado: str) -> Optional[str]:
    if modo == "subscribe" and token == token_esperado:
        return challenge
    return None


def parse_incoming(payload: dict) -> list:
    """Normaliza o payload bruto do webhook da Meta em uma lista de mensagens."""
    mensagens = []
    try:
        for entrada in payload.get("entry", []):
            for mudanca in entrada.get("changes", []):
                valor = mudanca.get("value", {})
                contatos = {c["wa_id"]: c.get("profile", {}).get("name") for c in valor.get("contacts", [])}
                for msg in valor.get("messages", []):
                    mensagens.append(_normalizar_mensagem(msg, contatos))
    except Exception:
        logger.exception("Erro ao normalizar payload do webhook")
        return []
    return mensagens


def _normalizar_mensagem(msg: dict, contatos: dict) -> dict:
    telefone = msg.get("from")
    tipo = msg.get("type")
    item = {
        "telefone": telefone,
        "nome": contatos.get(telefone),
        "tipo": tipo,
        "texto": None,
        "media_id": None,
        "mime_type": None,
        "message_id": msg.get("id"),
        "timestamp": msg.get("timestamp"),
    }
    if tipo == "text":
        item["texto"] = msg.get("text", {}).get("body")
    elif tipo in ("image", "document", "audio", "video"):
        media = msg.get(tipo, {})
        item["media_id"] = media.get("id")
        item["mime_type"] = media.get("mime_type")
        item["texto"] = media.get("caption")
    elif tipo == "button":
        item["texto"] = msg.get("button", {}).get("text")
    elif tipo == "interactive":
        interactive = msg.get("interactive", {})
        if interactive.get("type") == "button_reply":
            item["texto"] = interactive["button_reply"]["title"]
        elif interactive.get("type") == "list_reply":
            item["texto"] = interactive["list_reply"]["title"]
    return item
