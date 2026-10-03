from ...domain.entities.Pagamento import Pagamento
from ...domain.entities.Pedido import Pedido
from ...domain.repositories.CarrinhoRepository import CarrinhoRepository
from ...domain.repositories.PagamentoRepository import PagamentoRepository
from ...domain.repositories.PedidoRepository import PedidoRepository
from ...domain.value_objects.ItemPedido import ItemPedido
from .ConsultarFreteUseCase import ConsultarFreteUseCase


class CriarPedidoUseCase:
    def __init__(self, carrinho_repository: CarrinhoRepository, pedido_repository: PedidoRepository,
                 pagamento_repository: PagamentoRepository, consultar_frete_usecase: ConsultarFreteUseCase):
        self._carrinho_repository = carrinho_repository
        self._pedido_repository = pedido_repository
        self._pagamento_repository = pagamento_repository
        self._consultar_frete_usecase = consultar_frete_usecase

    def executar(self, cliente_id: str) -> Pedido:
        carrinho = self._carrinho_repository.buscar_por_cliente(cliente_id)
        carrinho.exigir_nao_vazio()

        subtotal = carrinho.subtotal
        frete = self._consultar_frete_usecase.executar()
        itens_pedido = [ItemPedido.a_partir_do_item_carrinho(item) for item in carrinho.itens]

        pedido = Pedido(
            numero_pedido=self._pedido_repository.proximo_numero(),
            cliente_id=cliente_id,
            itens=itens_pedido,
            subtotal=subtotal,
            frete=frete,
            total=subtotal + frete,
        )
        pedido = self._pedido_repository.salvar(pedido)

        pagamento = Pagamento(pedido_id=pedido.id, valor=pedido.total)
        self._pagamento_repository.salvar(pagamento)

        self._carrinho_repository.limpar(cliente_id)
        return pedido
