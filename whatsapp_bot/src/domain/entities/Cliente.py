from datetime import datetime
from typing import Optional

from ..value_objects.Telefone import Telefone


class Cliente:
    def __init__(self, whatsapp: Telefone, id: str = None, nome: str = None, cpf: str = None,
                 email: str = None, endereco: str = None, cidade: str = None, cep: str = None,
                 criado_em: Optional[datetime] = None, atualizado_em: Optional[datetime] = None):
        self.id = id
        self.whatsapp = whatsapp
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.endereco = endereco
        self.cidade = cidade
        self.cep = cep
        self.criado_em = criado_em or datetime.now()
        self.atualizado_em = atualizado_em or datetime.now()

    def atualizar_nome(self, nome: str) -> None:
        if nome and not self.nome:
            self.nome = nome
            self.atualizado_em = datetime.now()
