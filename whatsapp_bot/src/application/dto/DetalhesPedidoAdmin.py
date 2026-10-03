from dataclasses import dataclass
from typing import Optional

from ...domain.entities.Cliente import Cliente
from ...domain.entities.Pedido import Pedido


@dataclass
class DetalhesPedidoAdmin:
    pedido: Pedido
    cliente: Optional[Cliente]
