from dataclasses import dataclass
from typing import List

from ...domain.value_objects.Dinheiro import Dinheiro
from ...domain.value_objects.ItemCarrinho import ItemCarrinho


@dataclass
class ResumoCarrinho:
    itens: List[ItemCarrinho]
    subtotal: Dinheiro
    frete: Dinheiro
    total: Dinheiro
