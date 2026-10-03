from ..value_objects.Telefone import Telefone


class Administrador:
    def __init__(self, whatsapp: Telefone, id: str = None, nome: str = None, ativo: bool = True):
        self.id = id
        self.whatsapp = whatsapp
        self.nome = nome
        self.ativo = ativo
