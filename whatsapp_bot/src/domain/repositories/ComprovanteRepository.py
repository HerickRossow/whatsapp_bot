from abc import ABC, abstractmethod

from ..entities.Comprovante import Comprovante


class ComprovanteRepository(ABC):
    @abstractmethod
    def salvar(self, comprovante: Comprovante) -> Comprovante:
        ...
