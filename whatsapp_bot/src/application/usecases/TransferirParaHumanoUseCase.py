from ...domain.repositories.PedidoRepository import PedidoRepository


class TransferirParaHumanoUseCase:
    def __init__(self, pedido_repository: PedidoRepository):
        self._pedido_repository = pedido_repository

    def executar(self, cliente_id: str) -> None:
        pedido = self._pedido_repository.buscar_aberto_por_cliente(cliente_id)
        if pedido:
            pedido.transferir_para_humano()
            self._pedido_repository.salvar(pedido)
