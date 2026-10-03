from .DomainException import DomainException


class QuantidadeInvalidaError(DomainException):
    def __init__(self, quantidade: int):
        self.quantidade = quantidade
        super().__init__(f"Quantidade inválida: {quantidade}.")
