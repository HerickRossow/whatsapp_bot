from typing import Optional

import requests

from ...domain.gateways.WhatsAppGateway import WhatsAppGateway
from ...domain.value_objects.Telefone import Telefone
from ..config.Settings import Settings


class MetaWhatsAppGateway(WhatsAppGateway):
    def __init__(self, settings: Settings):
        self._settings = settings
        self._base_url = f"https://graph.facebook.com/{settings.whatsapp_api_version}"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._settings.whatsapp_token}",
            "Content-Type": "application/json",
        }

    def enviar_texto(self, telefone: Telefone, mensagem: str) -> None:
        url = f"{self._base_url}/{self._settings.whatsapp_phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": telefone.numero,
            "type": "text",
            "text": {"body": mensagem},
        }
        resposta = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if resposta.status_code >= 400:
            raise RuntimeError(f"Erro ao enviar texto para {telefone.numero}: {resposta.status_code} {resposta.text}")

    def enviar_imagem(self, telefone: Telefone, caminho_arquivo: str, legenda: Optional[str] = None,
                       mime_type: str = "image/jpeg") -> None:
        media_id = self._upload_midia(caminho_arquivo, mime_type)
        url = f"{self._base_url}/{self._settings.whatsapp_phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": telefone.numero,
            "type": "image",
            "image": {"id": media_id, **({"caption": legenda} if legenda else {})},
        }
        resposta = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        if resposta.status_code >= 400:
            raise RuntimeError(f"Erro ao enviar imagem para {telefone.numero}: {resposta.status_code} {resposta.text}")

    def baixar_midia(self, media_id: str) -> bytes:
        url_midia = self._obter_url_midia(media_id)
        resposta = requests.get(
            url_midia, headers={"Authorization": f"Bearer {self._settings.whatsapp_token}"}, timeout=60
        )
        if resposta.status_code >= 400:
            raise RuntimeError(f"Erro ao baixar mídia {media_id}: {resposta.status_code}")
        return resposta.content

    def _upload_midia(self, caminho_arquivo: str, mime_type: str) -> str:
        url = f"{self._base_url}/{self._settings.whatsapp_phone_number_id}/media"
        with open(caminho_arquivo, "rb") as arquivo:
            arquivos = {"file": (caminho_arquivo, arquivo, mime_type)}
            dados = {"messaging_product": "whatsapp", "type": mime_type}
            resposta = requests.post(
                url,
                headers={"Authorization": f"Bearer {self._settings.whatsapp_token}"},
                data=dados,
                files=arquivos,
                timeout=60,
            )
        if resposta.status_code >= 400:
            raise RuntimeError(f"Erro ao subir mídia: {resposta.status_code} {resposta.text}")
        return resposta.json()["id"]

    def _obter_url_midia(self, media_id: str) -> str:
        url = f"{self._base_url}/{media_id}"
        resposta = requests.get(url, headers=self._headers(), timeout=30)
        if resposta.status_code >= 400:
            raise RuntimeError(f"Erro ao obter URL da mídia {media_id}: {resposta.status_code} {resposta.text}")
        return resposta.json()["url"]
