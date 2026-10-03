from .Dinheiro import Dinheiro


class ItemCarrinho:
    def __init__(self, produto_id: str, nome: str, quantidade: int, preco_unitario: Dinheiro, sabor: str = None):
        self.produto_id = produto_id
        self.nome = nome
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.sabor = sabor

    @property
    def subtotal(self) -> Dinheiro:
        return self.preco_unitario * self.quantidade
