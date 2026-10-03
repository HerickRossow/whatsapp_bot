"""
Cliente da WhatsApp Business Cloud API (Meta).
Envia texto/imagem, baixa mídia recebida e normaliza o payload do webhook.
"""
import requests
import config

BASE_URL = f"https://graph.facebook.com/{config.WHATSAPP_API_VERSION}"


def _headers():
    return {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


def send_text(to: str, body: str):
    url = f"{BASE_URL}/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    r = requests.post(url, headers=_headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Erro ao enviar texto para {to}: {r.status_code} {r.text}")
    return r.json()


def upload_media(file_path: str, mime_type: str = "image/jpeg") -> str:
    """Sobe um arquivo para os servidores da Meta e devolve o media_id."""
    url = f"{BASE_URL}/{config.WHATSAPP_PHONE_NUMBER_ID}/media"
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, mime_type)}
        data = {"messaging_product": "whatsapp", "type": mime_type}
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
            data=data,
            files=files,
            timeout=60,
        )
    if r.status_code >= 400:
        raise RuntimeError(f"Erro ao subir mídia: {r.status_code} {r.text}")
    return r.json()["id"]


def send_image_by_path(to: str, file_path: str, caption: str = None, mime_type="image/jpeg"):
    media_id = upload_media(file_path, mime_type)
    url = f"{BASE_URL}/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"id": media_id, **({"caption": caption} if caption else {})},
    }
    r = requests.post(url, headers=_headers(), json=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Erro ao enviar imagem para {to}: {r.status_code} {r.text}")
    return r.json()


def get_media_url(media_id: str) -> str:
    url = f"{BASE_URL}/{media_id}"
    r = requests.get(url, headers=_headers(), timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Erro ao obter URL da mídia {media_id}: {r.status_code} {r.text}")
    return r.json()["url"]


def download_media(media_id: str) -> bytes:
    media_url = get_media_url(media_id)
    r = requests.get(media_url, headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"}, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"Erro ao baixar mídia {media_id}: {r.status_code}")
    return r.content


def verify_webhook(mode: str, token: str, challenge: str):
    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        return challenge
    return None


def parse_incoming(payload: dict):
    """
    Recebe o corpo bruto do webhook da Meta e devolve uma lista de mensagens
    normalizadas no formato:
    {telefone, nome, tipo, texto, media_id, mime_type, message_id, timestamp}
    """
    mensagens = []
    try:
        entradas = payload.get("entry", [])
        for entrada in entradas:
            for change in entrada.get("changes", []):
                valor = change.get("value", {})
                contatos = {c["wa_id"]: c.get("profile", {}).get("name") for c in valor.get("contacts", [])}
                for msg in valor.get("messages", []):
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
                    mensagens.append(item)
    except Exception as e:  # payload inesperado não deve derrubar o webhook
        print(f"[whatsapp_client] Erro ao normalizar payload: {e}")
    return mensagens
