from abc import ABC, abstractmethod
from typing import Optional

from ..entities.Pagamento import Pagamento


class PagamentoRepository(ABC):
    @abstractmethod
    def salvar(self, pagamento: Pagamento) -> Pagamento:
        ...

    @abstractmethod
    def buscar_por_pedido(self, pedido_id: str) -> Optional[Pagamento]:
        ...
