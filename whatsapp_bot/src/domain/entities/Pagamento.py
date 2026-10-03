from datetime import datetime
from typing import Optional

from ..enums.StatusPagamento import StatusPagamento
from ..value_objects.Dinheiro import Dinheiro


class Pagamento:
    def __init__(self, pedido_id: str, valor: Dinheiro, tipo: str = "PIX",
                 status: StatusPagamento = StatusPagamento.PENDENTE, id: str = None,
                 criado_em: Optional[datetime] = None, confirmado_em: Optional[datetime] = None):
        self.id = id
        self.pedido_id = pedido_id
        self.tipo = tipo
        self.valor = valor
        self.status = status
        self.criado_em = criado_em or datetime.now()
        self.confirmado_em = confirmado_em

    def confirmar(self) -> None:
        self.status = StatusPagamento.CONFIRMADO
        self.confirmado_em = datetime.now()

    def recusar(self) -> None:
        self.status = StatusPagamento.RECUSADO
