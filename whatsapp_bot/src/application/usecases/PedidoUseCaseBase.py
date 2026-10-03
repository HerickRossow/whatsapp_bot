from ...domain.entities.Pedido import Pedido
from ...domain.exceptions.PedidoNaoEncontradoError import PedidoNaoEncontradoError
from ...domain.gateways.WhatsAppGateway import WhatsAppGateway
from ...domain.repositories.ClienteRepository import ClienteRepository
from ...domain.repositories.PedidoRepository import PedidoRepository


class PedidoUseCaseBase:
    def __init__(self, pedido_repository: PedidoRepository, cliente_repository: ClienteRepository,
                 whatsapp_gateway: WhatsAppGateway):
        self._pedido_repository = pedido_repository
        self._cliente_repository = cliente_repository
        self._whatsapp_gateway = whatsapp_gateway

    def _buscar_pedido(self, numero_pedido: str) -> Pedido:
        pedido = self._pedido_repository.buscar_por_numero(numero_pedido)
        if pedido is None:
            raise PedidoNaoEncontradoError(numero_pedido)
        return pedido

    def _notificar_cliente(self, pedido: Pedido, mensagem: str) -> None:
        cliente = self._cliente_repository.buscar_por_id(pedido.cliente_id)
        if cliente:
            self._whatsapp_gateway.enviar_texto(cliente.whatsapp, mensagem)
