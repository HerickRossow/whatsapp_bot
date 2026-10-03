from ...domain.entities.Pedido import Pedido
from ...domain.repositories.PagamentoRepository import PagamentoRepository
from .PedidoUseCaseBase import PedidoUseCaseBase


class RecusarPagamentoUseCase(PedidoUseCaseBase):
    def __init__(self, pedido_repository, cliente_repository, whatsapp_gateway,
                 pagamento_repository: PagamentoRepository):
        super().__init__(pedido_repository, cliente_repository, whatsapp_gateway)
        self._pagamento_repository = pagamento_repository

    def executar(self, numero_pedido: str) -> Pedido:
        pedido = self._buscar_pedido(numero_pedido)

        pagamento = self._pagamento_repository.buscar_por_pedido(pedido.id)
        if pagamento:
            pagamento.recusar()
            self._pagamento_repository.salvar(pagamento)

        pedido.recusar_pagamento()
        self._pedido_repository.salvar(pedido)
        self._notificar_cliente(
            pedido,
            "Oi! Verificamos o comprovante, mas o pagamento ainda não pôde ser confirmado.\n\n"
            "Por favor, confira os dados do PIX e, se necessário, envie um novo comprovante. 👍",
        )
        return pedido
