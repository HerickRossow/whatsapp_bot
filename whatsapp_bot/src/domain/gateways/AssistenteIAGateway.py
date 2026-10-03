from abc import ABC, abstractmethod
from typing import List

from ..value_objects.RespostaAssistente import RespostaAssistente


class AssistenteIAGateway(ABC):
    @abstractmethod
    def obter_proxima_resposta(self, system: str, mensagens: list, ferramentas: List[dict]) -> RespostaAssistente:
        ...
