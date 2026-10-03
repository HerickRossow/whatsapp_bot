from abc import ABC, abstractmethod

from ..entities.Carrinho import Carrinho


class CarrinhoRepository(ABC):
    @abstractmethod
    def buscar_por_cliente(self, cliente_id: str) -> Carrinho:
        ...

    @abstractmethod
    def salvar(self, carrinho: Carrinho) -> None:
        ...

    @abstractmethod
    def limpar(self, cliente_id: str) -> None:
        ...
