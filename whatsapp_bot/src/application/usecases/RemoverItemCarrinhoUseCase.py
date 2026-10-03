from ...domain.entities.Carrinho import Carrinho
from ...domain.repositories.CarrinhoRepository import CarrinhoRepository


class RemoverItemCarrinhoUseCase:
    def __init__(self, carrinho_repository: CarrinhoRepository):
        self._carrinho_repository = carrinho_repository

    def executar(self, cliente_id: str, produto_id: str) -> Carrinho:
        carrinho = self._carrinho_repository.buscar_por_cliente(cliente_id)
        carrinho.remover_item(produto_id)
        self._carrinho_repository.salvar(carrinho)
        return carrinho
