from typing import Optional

from ...domain.entities.Produto import Produto
from ...domain.repositories.ProdutoRepository import ProdutoRepository


class ObterDetalhesProdutoUseCase:
    def __init__(self, produto_repository: ProdutoRepository):
        self._produto_repository = produto_repository

    def executar(self, produto_id: str) -> Optional[Produto]:
        return self._produto_repository.buscar_por_id(produto_id)
