from pathlib import Path

import openpyxl

from ...domain.entities.Produto import Produto
from ...domain.repositories.ProdutoRepository import ProdutoRepository
from ...domain.value_objects.Dinheiro import Dinheiro


class SincronizarCatalogoUseCase:
    def __init__(self, produto_repository: ProdutoRepository):
        self._produto_repository = produto_repository

    def executar(self, caminho_planilha: Path) -> int:
        if not caminho_planilha.exists():
            raise FileNotFoundError(f"Arquivo de produtos não encontrado: {caminho_planilha}")

        planilha = openpyxl.load_workbook(caminho_planilha, data_only=True).active
        cabecalho = [str(celula.value).strip() if celula.value else "" for celula in planilha[1]]
        indice = {nome: posicao for posicao, nome in enumerate(cabecalho)}

        total_sincronizado = 0
        for linha in planilha.iter_rows(min_row=2):
            if all(celula.value is None for celula in linha):
                continue
            sku = self._valor(linha, indice, "SKU")
            if not sku:
                continue

            produto_existente = self._produto_repository.buscar_por_sku(sku)
            produto = Produto(
                id=produto_existente.id if produto_existente else None,
                sku=sku,
                nome=str(self._valor(linha, indice, "Produto", "")),
                marca=str(self._valor(linha, indice, "Marca", "")),
                categoria=str(self._valor(linha, indice, "Categoria", "")),
                peso=str(self._valor(linha, indice, "Peso", "")),
                sabor=str(self._valor(linha, indice, "Sabor", "")),
                preco=self._parse_preco(self._valor(linha, indice, "Preço", 0)),
                estoque=int(self._valor(linha, indice, "Estoque", 0) or 0),
                descricao=str(self._valor(linha, indice, "Descricao", "")),
                imagem=str(self._valor(linha, indice, "Imagem", "")),
                ativo=str(self._valor(linha, indice, "Ativo", "SIM")).strip().upper() == "SIM",
            )
            self._produto_repository.salvar(produto)
            total_sincronizado += 1

        return total_sincronizado

    @staticmethod
    def _valor(linha, indice: dict, nome_coluna: str, default=""):
        posicao = indice.get(nome_coluna)
        if posicao is None or posicao >= len(linha):
            return default
        valor = linha[posicao].value
        return default if valor is None else valor

    @staticmethod
    def _parse_preco(valor) -> Dinheiro:
        if isinstance(valor, (int, float)):
            return Dinheiro(valor)
        texto = str(valor).strip().replace("R$", "").strip()
        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        elif "," in texto:
            texto = texto.replace(",", ".")
        try:
            return Dinheiro(texto)
        except (ValueError, ArithmeticError):
            return Dinheiro(0)
