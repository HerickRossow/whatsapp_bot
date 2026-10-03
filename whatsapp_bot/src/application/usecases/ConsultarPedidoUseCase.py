from typing import Optional

from ...domain.entities.Pedido import Pedido
from ...domain.repositories.PedidoRepository import PedidoRepository


class ConsultarPedidoUseCase:
    def __init__(self, pedido_repository: PedidoRepository):
        self._pedido_repository = pedido_repository

    def executar(self, cliente_id: str, numero_pedido: str = None) -> Optional[Pedido]:
        if numero_pedido:
            pedido = self._pedido_repository.buscar_por_numero(numero_pedido)
            if pedido is None or pedido.cliente_id != cliente_id:
                return None
            return pedido
        return self._pedido_repository.buscar_mais_recente_por_cliente(cliente_id)
