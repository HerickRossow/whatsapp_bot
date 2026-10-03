from typing import List, Optional

from .ChamadaFerramenta import ChamadaFerramenta


class RespostaAssistente:
    def __init__(self, mensagens: list, texto_final: Optional[str] = None,
                 chamadas_ferramenta: Optional[List[ChamadaFerramenta]] = None):
        self.mensagens = mensagens
        self.texto_final = texto_final
        self.chamadas_ferramenta = chamadas_ferramenta or []

    @property
    def finalizada(self) -> bool:
        return not self.chamadas_ferramenta
