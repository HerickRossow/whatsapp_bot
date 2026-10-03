"""
Camada de acesso ao SQLite.
Cria as tabelas e oferece funções auxiliares usadas pelo resto do sistema.
Isso substitui o que seria feito nos workflows WF00/WF02 do n8n.
"""
import sqlite3
import threading
from datetime import datetime

import config


_local = threading.local()


def get_conn():
    """Retorna uma conexão SQLite por thread (Flask roda com threads)."""
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(str(config.DB_PATH), check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA foreign_keys = ON;")
    return _local.conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    # configurações padrão vindas do .env, se ainda não existirem
    defaults = {
        "PIX_CHAVE": config.PIX_CHAVE,
        "PIX_NOME": config.PIX_NOME,
        "PIX_BANCO": config.PIX_BANCO,
        "ADMIN_WHATSAPP": config.ADMIN_WHATSAPP,
        "NOME_LOJA": config.NOME_LOJA,
        "FRETE_PADRAO": str(config.FRETE_PADRAO),
    }
    for chave, valor in defaults.items():
        conn.execute(
            "INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?, ?)",
            (chave, valor),
        )
    if config.ADMIN_WHATSAPP:
        conn.execute(
            "INSERT OR IGNORE INTO administradores (whatsapp, nome, ativo) VALUES (?, ?, 1)",
            (config.ADMIN_WHATSAPP, config.ADMIN_NOME),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# Configurações
# ---------------------------------------------------------------------------
def get_config(chave, default=None):
    conn = get_conn()
    row = conn.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,)).fetchone()
    return row["valor"] if row else default


def set_config(chave, valor):
    conn = get_conn()
    conn.execute(
        "INSERT INTO configuracoes (chave, valor) VALUES (?, ?) "
        "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
        (chave, valor),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Administradores
# ---------------------------------------------------------------------------
def is_admin(whatsapp: str) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT 1 FROM administradores WHERE whatsapp = ? AND ativo = 1", (whatsapp,)
    ).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------
def get_or_create_cliente(whatsapp: str, nome: str = None):
    conn = get_conn()
    row = conn.execute("SELECT * FROM clientes WHERE whatsapp = ?", (whatsapp,)).fetchone()
    if row:
        if nome and not row["nome"]:
            conn.execute(
                "UPDATE clientes SET nome = ?, atualizado_em = datetime('now') WHERE id = ?",
                (nome, row["id"]),
            )
            conn.commit()
        return dict(conn.execute("SELECT * FROM clientes WHERE id = ?", (row["id"],)).fetchone())
    cur = conn.execute(
        "INSERT INTO clientes (whatsapp, nome) VALUES (?, ?)", (whatsapp, nome)
    )
    conn.commit()
    return dict(conn.execute("SELECT * FROM clientes WHERE id = ?", (cur.lastrowid,)).fetchone())


# ---------------------------------------------------------------------------
# Conversas (memória do bot)
# ---------------------------------------------------------------------------
def salvar_mensagem(cliente_id, tipo, mensagem, origem):
    """origem: 'cliente' ou 'bot'"""
    conn = get_conn()
    conn.execute(
        "INSERT INTO conversas (cliente_id, tipo, mensagem, origem) VALUES (?, ?, ?, ?)",
        (cliente_id, tipo, mensagem, origem),
    )
    conn.commit()


def get_historico(cliente_id, limit=20):
    conn = get_conn()
    rows = conn.execute(
        "SELECT tipo, mensagem, origem, criado_em FROM conversas "
        "WHERE cliente_id = ? ORDER BY id DESC LIMIT ?",
        (cliente_id, limit),
    ).fetchall()
    return [dict(r) for r in reversed(rows)]


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------
def get_pedido_aberto(cliente_id):
    import status as st
    conn = get_conn()
    placeholders = ",".join("?" for _ in st.ABERTOS)
    row = conn.execute(
        f"SELECT * FROM pedidos WHERE cliente_id = ? AND status IN ({placeholders}) "
        "ORDER BY id DESC LIMIT 1",
        (cliente_id, *st.ABERTOS),
    ).fetchone()
    return dict(row) if row else None


def get_pedido_por_numero(numero_pedido):
    conn = get_conn()
    row = conn.execute("SELECT * FROM pedidos WHERE numero_pedido = ?", (numero_pedido,)).fetchone()
    return dict(row) if row else None


def gerar_numero_pedido():
    conn = get_conn()
    row = conn.execute("SELECT MAX(id) AS m FROM pedidos").fetchone()
    proximo = (row["m"] or 0) + 1
    return f"{proximo:06d}"


def registrar_erro(origem, pedido_numero, mensagem):
    conn = get_conn()
    conn.execute(
        "INSERT INTO erros (origem, pedido_numero, mensagem) VALUES (?, ?, ?)",
        (origem, pedido_numero, mensagem),
    )
    conn.commit()
