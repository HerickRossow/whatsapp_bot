from typing import List, Optional

from ..exceptions.CarrinhoVazioError import CarrinhoVazioError
from ..exceptions.EstoqueInsuficienteError import EstoqueInsuficienteError
from ..exceptions.QuantidadeInvalidaError import QuantidadeInvalidaError
from ..value_objects.Dinheiro import Dinheiro
from ..value_objects.ItemCarrinho import ItemCarrinho
from .Produto import Produto


class Carrinho:
    def __init__(self, cliente_id: str, itens: Optional[List[ItemCarrinho]] = None):
        self.cliente_id = cliente_id
        self.itens = itens or []

    @property
    def esta_vazio(self) -> bool:
        return not self.itens

    @property
    def subtotal(self) -> Dinheiro:
        total = Dinheiro(0)
        for item in self.itens:
            total = total + item.subtotal
        return total

    def adicionar_item(self, produto: Produto, quantidade: int, sabor: str = None) -> None:
        if quantidade <= 0:
            raise QuantidadeInvalidaError(quantidade)
        if not produto.esta_disponivel(quantidade):
            raise EstoqueInsuficienteError(produto.nome, produto.estoque)
        self.itens.append(ItemCarrinho(produto.id, produto.nome, quantidade, produto.preco, sabor))

    def remover_item(self, produto_id: str) -> None:
        self.itens = [item for item in self.itens if item.produto_id != produto_id]

    def esvaziar(self) -> None:
        self.itens = []

    def exigir_nao_vazio(self) -> None:
        if self.esta_vazio:
            raise CarrinhoVazioError()
