from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.Produto import Produto


class ProdutoRepository(ABC):
    @abstractmethod
    def buscar_por_id(self, produto_id: str) -> Optional[Produto]:
        ...

    @abstractmethod
    def buscar_por_termo(self, termo: str, limite: int = 15) -> List[Produto]:
        ...

    @abstractmethod
    def salvar(self, produto: Produto) -> Produto:
        ...
