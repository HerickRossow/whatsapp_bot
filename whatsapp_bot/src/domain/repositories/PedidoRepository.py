from abc import ABC, abstractmethod
from typing import Optional

from ..entities.Pedido import Pedido


class PedidoRepository(ABC):
    @abstractmethod
    def proximo_numero(self) -> str:
        ...

    @abstractmethod
    def salvar(self, pedido: Pedido) -> Pedido:
        ...

    @abstractmethod
    def buscar_por_numero(self, numero_pedido: str) -> Optional[Pedido]:
        ...

    @abstractmethod
    def buscar_aberto_por_cliente(self, cliente_id: str) -> Optional[Pedido]:
        ...
