from ...domain.entities.Pedido import Pedido
from ...domain.repositories.PagamentoRepository import PagamentoRepository
from ...domain.repositories.ProdutoRepository import ProdutoRepository
from .PedidoUseCaseBase import PedidoUseCaseBase


class ConfirmarPagamentoUseCase(PedidoUseCaseBase):
    def __init__(self, pedido_repository, cliente_repository, whatsapp_gateway,
                 pagamento_repository: PagamentoRepository, produto_repository: ProdutoRepository):
        super().__init__(pedido_repository, cliente_repository, whatsapp_gateway)
        self._pagamento_repository = pagamento_repository
        self._produto_repository = produto_repository

    def executar(self, numero_pedido: str) -> Pedido:
        pedido = self._buscar_pedido(numero_pedido)
        pedido.confirmar_pagamento()

        pagamento = self._pagamento_repository.buscar_por_pedido(pedido.id)
        if pagamento:
            pagamento.confirmar()
            self._pagamento_repository.salvar(pagamento)

        for item in pedido.itens:
            produto = self._produto_repository.buscar_por_id(item.produto_id)
            if produto and produto.estoque >= item.quantidade:
                produto.baixar_estoque(item.quantidade)
                self._produto_repository.salvar(produto)

        self._pedido_repository.salvar(pedido)
        self._notificar_cliente(
            pedido,
            f"✅ Pagamento confirmado!\n\nSeu pedido #{pedido.numero_pedido} foi aprovado.\n\n"
            "Estamos separando seus produtos. 👊\n\nAssim que estiver pronto para envio, avisaremos você.",
        )
        return pedido
