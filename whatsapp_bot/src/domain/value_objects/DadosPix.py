class DadosPix:
    __slots__ = ("chave", "nome", "banco")

    def __init__(self, chave: str, nome: str, banco: str):
        self.chave = chave
        self.nome = nome
        self.banco = banco
