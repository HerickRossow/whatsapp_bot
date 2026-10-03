from abc import ABC, abstractmethod
from typing import List

from ..entities.Conversa import Conversa


class ConversaRepository(ABC):
    @abstractmethod
    def salvar(self, conversa: Conversa) -> None:
        ...

    @abstractmethod
    def buscar_historico(self, cliente_id: str, limite: int = 20) -> List[Conversa]:
        ...
