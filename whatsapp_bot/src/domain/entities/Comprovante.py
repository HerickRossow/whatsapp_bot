from datetime import datetime
from typing import Optional


class Comprovante:
    def __init__(self, pedido_id: str, cliente_id: str, arquivo: str, nome_arquivo: str,
                 status: str = "AGUARDANDO_CONFERENCIA", id: str = None,
                 data_recebimento: Optional[datetime] = None):
        self.id = id
        self.pedido_id = pedido_id
        self.cliente_id = cliente_id
        self.arquivo = arquivo
        self.nome_arquivo = nome_arquivo
        self.status = status
        self.data_recebimento = data_recebimento or datetime.now()
