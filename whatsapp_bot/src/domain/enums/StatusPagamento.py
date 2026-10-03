from enum import Enum


class StatusPagamento(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    RECUSADO = "RECUSADO"
