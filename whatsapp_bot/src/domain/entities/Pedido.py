from datetime import datetime
from typing import List, Optional

from ..enums.StatusPedido import StatusPedido
from ..exceptions.TransicaoInvalidaError import TransicaoInvalidaError
from ..value_objects.Dinheiro import Dinheiro
from ..value_objects.ItemPedido import ItemPedido


class Pedido:
    def __init__(self, numero_pedido: str, cliente_id: str, itens: List[ItemPedido], subtotal: Dinheiro,
                 frete: Dinheiro, total: Dinheiro, status: StatusPedido = StatusPedido.AGUARDANDO_PAGAMENTO,
                 id: str = None, rastreamento: Optional[str] = None, criado_em: Optional[datetime] = None,
                 atualizado_em: Optional[datetime] = None):
        self.id = id
        self.numero_pedido = numero_pedido
        self.cliente_id = cliente_id
        self.itens = itens
        self.subtotal = subtotal
        self.frete = frete
        self.total = total
        self.status = status
        self.rastreamento = rastreamento
        self.criado_em = criado_em or datetime.now()
        self.atualizado_em = atualizado_em or datetime.now()

    def _mudar_status(self, novo_status: StatusPedido) -> None:
        self.status = novo_status
        self.atualizado_em = datetime.now()

    def confirmar_pagamento(self) -> None:
        if self.status not in (StatusPedido.COMPROVANTE_RECEBIDO, StatusPedido.AGUARDANDO_CONFERENCIA):
            raise TransicaoInvalidaError(self.status, "confirmar pagamento")
        self._mudar_status(StatusPedido.PAGAMENTO_CONFIRMADO)

    def recusar_pagamento(self) -> None:
        self._mudar_status(StatusPedido.PAGAMENTO_NAO_CONFIRMADO)

    def marcar_comprovante_recebido(self) -> None:
        self._mudar_status(StatusPedido.COMPROVANTE_RECEBIDO)

    def marcar_pronto(self) -> None:
        self._mudar_status(StatusPedido.PRONTO)

    def enviar(self, codigo_rastreamento: str) -> None:
        if not codigo_rastreamento:
            raise ValueError("Código de rastreamento é obrigatório para marcar o pedido como enviado.")
        self.rastreamento = codigo_rastreamento
        self._mudar_status(StatusPedido.ENVIADO)

    def cancelar(self) -> None:
        self._mudar_status(StatusPedido.CANCELADO)

    def transferir_para_humano(self) -> None:
        self._mudar_status(StatusPedido.HUMANO)
