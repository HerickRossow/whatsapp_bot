from typing import Optional

from ...domain.enums.StatusPedido import StatusPedido
from ...domain.repositories.PedidoRepository import PedidoRepository


class ConsultarStatusPedidoUseCase:
    def __init__(self, pedido_repository: PedidoRepository):
        self._pedido_repository = pedido_repository

    def executar(self, numero_pedido: str) -> Optional[StatusPedido]:
        pedido = self._pedido_repository.buscar_por_numero(numero_pedido)
        return pedido.status if pedido else None
