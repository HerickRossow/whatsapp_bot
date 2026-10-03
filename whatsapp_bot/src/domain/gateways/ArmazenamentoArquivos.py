from abc import ABC, abstractmethod


class ArmazenamentoArquivos(ABC):
    @abstractmethod
    def salvar(self, nome_arquivo: str, conteudo: bytes) -> str:
        ...
