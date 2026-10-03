"""
Sincroniza o catálogo de produtos do Excel (produtos.xlsx) para o SQLite.
Você edita o Excel; este script (ou a rota /sync-produtos) atualiza o banco.

Uso:
    python excel_sync.py            # sincroniza o arquivo configurado em config.PRODUTOS_XLSX
    python excel_sync.py --criar-exemplo   # cria um produtos.xlsx de exemplo, se não existir
    Deletar todos os arquivos da pasta old_project
"""
import sys
import openpyxl

import config
import db

COLUNAS = ["ID", "SKU", "Produto", "Marca", "Categoria", "Peso", "Sabor",
           "Preço", "Estoque", "Descricao", "Imagem", "Ativo"]

EXEMPLO_LINHAS = [
    [1, "CR001", "Creatina", "Growth", "Creatina", "250g", "-", "79,90", 10, "Creatina monoidratada", "creatina.jpg", "SIM"],
    [2, "WHEY01", "Whey Protein", "Growth", "Whey", "1kg", "Chocolate", "119,90", 5, "Whey concentrado", "whey.jpg", "SIM"],
    [3, "WHEY02", "Whey Protein", "Growth", "Whey", "1kg", "Baunilha", "119,90", 8, "Whey concentrado", "whey.jpg", "SIM"],
    [4, "BCAA01", "BCAA 2:1:1", "Max Titanium", "Aminoácido", "150 caps", "-", "49,90", 12, "BCAA em cápsulas", "bcaa.jpg", "SIM"],
]


def criar_exemplo(caminho=None):
    caminho = caminho or config.PRODUTOS_XLSX
    if caminho.exists():
        print(f"Já existe um arquivo em {caminho}, nada foi feito.")
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Produtos"
    ws.append(COLUNAS)
    for linha in EXEMPLO_LINHAS:
        ws.append(linha)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    wb.save(caminho)
    print(f"Arquivo de exemplo criado em {caminho}")


def _num_preco(valor):
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip()
    texto = texto.replace("R$", "").strip()
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return 0.0


def sincronizar(caminho=None):
    caminho = caminho or config.PRODUTOS_XLSX
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de produtos não encontrado: {caminho}")

    wb = openpyxl.load_workbook(caminho, data_only=True)
    ws = wb.active

    cabecalho = [str(c.value).strip() if c.value else "" for c in ws[1]]
    idx = {nome: i for i, nome in enumerate(cabecalho)}

    def val(row, nome, default=""):
        i = idx.get(nome)
        if i is None or i >= len(row):
            return default
        v = row[i].value
        return default if v is None else v

    conn = db.get_conn()
    total = 0
    for row in ws.iter_rows(min_row=2):
        if all(c.value is None for c in row):
            continue
        produto_id = val(row, "ID")
        if produto_id in (None, ""):
            continue
        conn.execute(
            """
            INSERT INTO produtos (id, sku, nome, marca, categoria, peso, sabor, preco,
                                   estoque, descricao, imagem, ativo, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                sku=excluded.sku, nome=excluded.nome, marca=excluded.marca,
                categoria=excluded.categoria, peso=excluded.peso, sabor=excluded.sabor,
                preco=excluded.preco, estoque=excluded.estoque, descricao=excluded.descricao,
                imagem=excluded.imagem, ativo=excluded.ativo, atualizado_em=datetime('now')
            """,
            (
                int(produto_id),
                str(val(row, "SKU", "")),
                str(val(row, "Produto", "")),
                str(val(row, "Marca", "")),
                str(val(row, "Categoria", "")),
                str(val(row, "Peso", "")),
                str(val(row, "Sabor", "")),
                _num_preco(val(row, "Preço", val(row, "preco", 0))),
                int(val(row, "Estoque", 0) or 0),
                str(val(row, "Descricao", "")),
                str(val(row, "Imagem", "")),
                str(val(row, "Ativo", "SIM")),
            ),
        )
        total += 1
    conn.commit()
    print(f"{total} produtos sincronizados a partir de {caminho}")
    return total


if __name__ == "__main__":
    db.init_db()
    if "--criar-exemplo" in sys.argv:
        criar_exemplo()
    else:
        sincronizar()
