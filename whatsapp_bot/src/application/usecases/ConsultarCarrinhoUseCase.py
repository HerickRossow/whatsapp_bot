from ...domain.entities.Carrinho import Carrinho
from ...domain.repositories.CarrinhoRepository import CarrinhoRepository


class ConsultarCarrinhoUseCase:
    def __init__(self, carrinho_repository: CarrinhoRepository):
        self._carrinho_repository = carrinho_repository

    def executar(self, cliente_id: str) -> Carrinho:
        return self._carrinho_repository.buscar_por_cliente(cliente_id)
