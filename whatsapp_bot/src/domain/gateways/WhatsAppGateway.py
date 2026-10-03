from abc import ABC, abstractmethod
from typing import Optional

from ..value_objects.Telefone import Telefone


class WhatsAppGateway(ABC):
    @abstractmethod
    def enviar_texto(self, telefone: Telefone, mensagem: str) -> None:
        ...

    @abstractmethod
    def enviar_imagem(self, telefone: Telefone, caminho_arquivo: str, legenda: Optional[str] = None,
                       mime_type: str = "image/jpeg") -> None:
        ...

    @abstractmethod
    def baixar_midia(self, media_id: str) -> bytes:
        ...
