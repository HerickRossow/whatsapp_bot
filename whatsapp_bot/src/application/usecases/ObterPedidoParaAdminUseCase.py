from typing import Optional

from ...domain.repositories.ClienteRepository import ClienteRepository
from ...domain.repositories.PedidoRepository import PedidoRepository
from ..dto.DetalhesPedidoAdmin import DetalhesPedidoAdmin


class ObterPedidoParaAdminUseCase:
    def __init__(self, pedido_repository: PedidoRepository, cliente_repository: ClienteRepository):
        self._pedido_repository = pedido_repository
        self._cliente_repository = cliente_repository

    def executar(self, numero_pedido: str) -> Optional[DetalhesPedidoAdmin]:
        pedido = self._pedido_repository.buscar_por_numero(numero_pedido)
        if pedido is None:
            return None
        cliente = self._cliente_repository.buscar_por_id(pedido.cliente_id)
        return DetalhesPedidoAdmin(pedido=pedido, cliente=cliente)
