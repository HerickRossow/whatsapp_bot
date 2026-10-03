from ...domain.entities.Pedido import Pedido
from .PedidoUseCaseBase import PedidoUseCaseBase


class MarcarPedidoProntoUseCase(PedidoUseCaseBase):
    def executar(self, numero_pedido: str) -> Pedido:
        pedido = self._buscar_pedido(numero_pedido)
        pedido.marcar_pronto()
        self._pedido_repository.salvar(pedido)
        self._notificar_cliente(
            pedido,
            f"📦 Pedido #{pedido.numero_pedido} pronto!\n\nSeu pedido já está separado e disponível para envio/retirada.",
        )
        return pedido
