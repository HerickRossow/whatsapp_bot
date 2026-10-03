import re

_DIGITOS_RE = re.compile(r"\D+")


class Telefone:
    __slots__ = ("_numero",)

    def __init__(self, numero: str):
        limpo = _DIGITOS_RE.sub("", numero or "")
        if len(limpo) < 10:
            raise ValueError(f"Número de WhatsApp inválido: {numero!r}")
        self._numero = limpo

    @property
    def numero(self) -> str:
        return self._numero

    def __eq__(self, outro) -> bool:
        return isinstance(outro, Telefone) and self._numero == outro._numero

    def __hash__(self) -> int:
        return hash(self._numero)

    def __repr__(self) -> str:
        return f"Telefone({self._numero})"
