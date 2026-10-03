from datetime import datetime
from typing import Optional


class Conversa:
    def __init__(self, cliente_id: str, tipo: str, mensagem: str, origem: str,
                 id: str = None, criado_em: Optional[datetime] = None):
        self.id = id
        self.cliente_id = cliente_id
        self.tipo = tipo
        self.mensagem = mensagem
        self.origem = origem
        self.criado_em = criado_em or datetime.now()
