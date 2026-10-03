from datetime import datetime
from pathlib import Path

from ...domain.gateways.ArmazenamentoArquivos import ArmazenamentoArquivos


class ArmazenamentoLocalArquivos(ArmazenamentoArquivos):
    def __init__(self, diretorio_base: Path):
        self._diretorio_base = diretorio_base

    def salvar(self, nome_arquivo: str, conteudo: bytes) -> str:
        hoje = datetime.now()
        pasta = self._diretorio_base / f"{hoje:%Y}" / f"{hoje:%m}" / f"{hoje:%d}"
        pasta.mkdir(parents=True, exist_ok=True)
        caminho = pasta / nome_arquivo
        caminho.write_bytes(conteudo)
        return str(caminho)
