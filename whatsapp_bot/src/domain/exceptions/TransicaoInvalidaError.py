from .DomainException import DomainException


class TransicaoInvalidaError(DomainException):
    def __init__(self, status_atual, acao: str):
        self.status_atual = status_atual
        self.acao = acao
        super().__init__(f"Não é possível {acao} com o pedido no status '{status_atual}'.")
