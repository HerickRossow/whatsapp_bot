from ...domain.entities.Carrinho import Carrinho
from ...domain.exceptions.ProdutoNaoEncontradoError import ProdutoNaoEncontradoError
from ...domain.repositories.CarrinhoRepository import CarrinhoRepository
from ...domain.repositories.ProdutoRepository import ProdutoRepository


class AdicionarItemCarrinhoUseCase:
    def __init__(self, carrinho_repository: CarrinhoRepository, produto_repository: ProdutoRepository):
        self._carrinho_repository = carrinho_repository
        self._produto_repository = produto_repository

    def executar(self, cliente_id: str, produto_id: str, quantidade: int, sabor: str = None) -> Carrinho:
        produto = self._produto_repository.buscar_por_id(produto_id)
        if produto is None:
            raise ProdutoNaoEncontradoError(produto_id)

        carrinho = self._carrinho_repository.buscar_por_cliente(cliente_id)
        carrinho.adicionar_item(produto, quantidade, sabor)
        self._carrinho_repository.salvar(carrinho)
        return carrinho
