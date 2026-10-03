from .DomainException import DomainException


class CarrinhoVazioError(DomainException):
    def __init__(self):
        super().__init__("O carrinho está vazio.")
