from typing import List

from ...domain.entities.Produto import Produto
from ...domain.repositories.ProdutoRepository import ProdutoRepository


class BuscarProdutosUseCase:
    def __init__(self, produto_repository: ProdutoRepository):
        self._produto_repository = produto_repository

    def executar(self, termo: str) -> List[Produto]:
        return self._produto_repository.buscar_por_termo(termo)
