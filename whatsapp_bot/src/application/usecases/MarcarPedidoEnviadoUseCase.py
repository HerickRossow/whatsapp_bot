from ...domain.entities.Pedido import Pedido
from .PedidoUseCaseBase import PedidoUseCaseBase


class MarcarPedidoEnviadoUseCase(PedidoUseCaseBase):
    def executar(self, numero_pedido: str, codigo_rastreamento: str) -> Pedido:
        pedido = self._buscar_pedido(numero_pedido)
        pedido.enviar(codigo_rastreamento)
        self._pedido_repository.salvar(pedido)
        self._notificar_cliente(
            pedido,
            f"🚚 Seu pedido #{pedido.numero_pedido} foi enviado!\n\n📦 Código de rastreio:\n{codigo_rastreamento}",
        )
        return pedido
