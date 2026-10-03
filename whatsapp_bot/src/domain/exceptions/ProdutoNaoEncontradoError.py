from .DomainException import DomainException


class ProdutoNaoEncontradoError(DomainException):
    def __init__(self, produto_id: str):
        self.produto_id = produto_id
        super().__init__(f"Produto não encontrado: {produto_id}.")
