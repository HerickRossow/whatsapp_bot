from ..exceptions.EstoqueInsuficienteError import EstoqueInsuficienteError
from ..value_objects.Dinheiro import Dinheiro


class Produto:
    def __init__(self, nome: str, preco: Dinheiro, estoque: int, id: str = None, sku: str = None,
                 marca: str = None, categoria: str = None, peso: str = None, sabor: str = None,
                 descricao: str = None, imagem: str = None, ativo: bool = True):
        self.id = id
        self.sku = sku
        self.nome = nome
        self.marca = marca
        self.categoria = categoria
        self.peso = peso
        self.sabor = sabor
        self.preco = preco
        self.estoque = estoque
        self.descricao = descricao
        self.imagem = imagem
        self.ativo = ativo

    def esta_disponivel(self, quantidade: int) -> bool:
        return self.ativo and self.estoque >= quantidade

    def baixar_estoque(self, quantidade: int) -> None:
        if self.estoque < quantidade:
            raise EstoqueInsuficienteError(self.nome, self.estoque)
        self.estoque -= quantidade
