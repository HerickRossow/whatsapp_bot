from abc import ABC, abstractmethod
from typing import Optional


class ConfiguracaoRepository(ABC):
    @abstractmethod
    def obter(self, chave: str, default: Optional[str] = None) -> Optional[str]:
        ...

    @abstractmethod
    def definir(self, chave: str, valor: str) -> None:
        ...
