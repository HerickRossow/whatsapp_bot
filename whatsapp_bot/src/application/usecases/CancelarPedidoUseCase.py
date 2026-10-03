from ...domain.entities.Pedido import Pedido
from .PedidoUseCaseBase import PedidoUseCaseBase


class CancelarPedidoUseCase(PedidoUseCaseBase):
    def executar(self, numero_pedido: str) -> Pedido:
        pedido = self._buscar_pedido(numero_pedido)
        pedido.cancelar()
        self._pedido_repository.salvar(pedido)
        self._notificar_cliente(pedido, f"Seu pedido #{pedido.numero_pedido} foi cancelado.")
        return pedido
