from decimal import Decimal, ROUND_HALF_UP


class Dinheiro:
    __slots__ = ("_valor",)

    def __init__(self, valor):
        self._valor = Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def valor(self) -> float:
        return float(self._valor)

    def __add__(self, outro: "Dinheiro") -> "Dinheiro":
        return Dinheiro(self._valor + outro._valor)

    def __mul__(self, quantidade: int) -> "Dinheiro":
        return Dinheiro(self._valor * quantidade)

    def __eq__(self, outro) -> bool:
        return isinstance(outro, Dinheiro) and self._valor == outro._valor

    def __lt__(self, outro: "Dinheiro") -> bool:
        return self._valor < outro._valor

    def __repr__(self) -> str:
        return f"Dinheiro({self._valor})"
