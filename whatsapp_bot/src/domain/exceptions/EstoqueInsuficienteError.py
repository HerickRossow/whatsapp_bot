from .DomainException import DomainException


class EstoqueInsuficienteError(DomainException):
    def __init__(self, produto_nome: str, estoque_disponivel: int):
        self.produto_nome = produto_nome
        self.estoque_disponivel = estoque_disponivel
        super().__init__(f"Estoque insuficiente para '{produto_nome}': disponível {estoque_disponivel}.")
