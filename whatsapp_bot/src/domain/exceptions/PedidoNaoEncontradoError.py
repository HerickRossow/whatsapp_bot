from .DomainException import DomainException


class PedidoNaoEncontradoError(DomainException):
    def __init__(self, numero_pedido: str):
        self.numero_pedido = numero_pedido
        super().__init__(f"Pedido não encontrado: {numero_pedido}.")
