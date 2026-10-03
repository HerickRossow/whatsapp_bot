"""
Ferramentas (tools) que o Claude pode chamar durante a conversa.

Regra de ouro do projeto: o Claude NUNCA inventa preço, estoque ou status de
pagamento. Toda informação factual passa por aqui, que consulta o SQLite.

O cliente_id é sempre amarrado pelo próprio backend (nunca fornecido pelo
Claude), para que um cliente jamais possa manipular o pedido de outro.
"""
import db
import config
import status as st


def buscar_produtos(consulta: str):
    conn = db.get_conn()
    like = f"%{consulta}%"
    rows = conn.execute(
        """
        SELECT id, sku, nome, marca, categoria, peso, sabor, preco, estoque
        FROM produtos
        WHERE ativo = 'SIM' AND estoque > 0
        AND (nome LIKE ? OR marca LIKE ? OR categoria LIKE ? OR sabor LIKE ?)
        ORDER BY nome
        LIMIT 15
        """,
        (like, like, like, like),
    ).fetchall()
    produtos = [dict(r) for r in rows]
    if not produtos:
        return {"encontrados": 0, "produtos": []}
    return {"encontrados": len(produtos), "produtos": produtos}


def buscar_produto(produto_id: int):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    if not row:
        return {"erro": "produto_nao_encontrado"}
    return dict(row)


def consultar_estoque(produto_id: int):
    conn = db.get_conn()
    row = conn.execute("SELECT nome, estoque FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    if not row:
        return {"erro": "produto_nao_encontrado"}
    return dict(row)


def _cliente_do_carrinho(conn, cliente_id):
    rows = conn.execute(
        """
        SELECT c.id AS carrinho_id, p.id AS produto_id, p.nome, p.marca, p.peso,
               c.sabor, c.quantidade, c.preco_unitario,
               (c.quantidade * c.preco_unitario) AS subtotal
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.cliente_id = ?
        """,
        (cliente_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def consultar_carrinho(cliente_id: int):
    conn = db.get_conn()
    itens = _cliente_do_carrinho(conn, cliente_id)
    total = sum(i["subtotal"] for i in itens)
    return {"itens": itens, "subtotal": round(total, 2)}


def adicionar_carrinho(cliente_id: int, produto_id: int, quantidade: int, sabor: str = None):
    conn = db.get_conn()
    produto = conn.execute("SELECT * FROM produtos WHERE id = ? AND ativo = 'SIM'", (produto_id,)).fetchone()
    if not produto:
        return {"erro": "produto_nao_encontrado"}
    if quantidade <= 0:
        return {"erro": "quantidade_invalida"}
    if produto["estoque"] < quantidade:
        return {"erro": "estoque_insuficiente", "estoque_disponivel": produto["estoque"]}
    conn.execute(
        "INSERT INTO carrinho (cliente_id, produto_id, quantidade, preco_unitario, sabor) "
        "VALUES (?, ?, ?, ?, ?)",
        (cliente_id, produto_id, quantidade, produto["preco"], sabor),
    )
    conn.commit()
    return {"ok": True, "carrinho": consultar_carrinho(cliente_id)}


def remover_carrinho(cliente_id: int, produto_id: int):
    conn = db.get_conn()
    conn.execute(
        "DELETE FROM carrinho WHERE cliente_id = ? AND produto_id = ?", (cliente_id, produto_id)
    )
    conn.commit()
    return {"ok": True, "carrinho": consultar_carrinho(cliente_id)}


def calcular_carrinho(cliente_id: int):
    """O n8n (aqui, o Python) faz a conta -- o Claude nunca calcula valores."""
    conn = db.get_conn()
    itens = _cliente_do_carrinho(conn, cliente_id)
    subtotal = round(sum(i["subtotal"] for i in itens), 2)
    frete = float(db.get_config("FRETE_PADRAO", config.FRETE_PADRAO))
    total = round(subtotal + frete, 2)
    return {"itens": itens, "subtotal": subtotal, "frete": frete, "total": total}


def consultar_frete(cliente_id: int):
    frete = float(db.get_config("FRETE_PADRAO", config.FRETE_PADRAO))
    return {"frete": frete}


def criar_pedido(cliente_id: int):
    """Fecha o carrinho atual em um pedido AGUARDANDO_PAGAMENTO e devolve os dados do PIX."""
    conn = db.get_conn()
    itens = _cliente_do_carrinho(conn, cliente_id)
    if not itens:
        return {"erro": "carrinho_vazio"}

    calculo = calcular_carrinho(cliente_id)
    numero_pedido = db.gerar_numero_pedido()

    cur = conn.execute(
        "INSERT INTO pedidos (numero_pedido, cliente_id, subtotal, frete, total, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (numero_pedido, cliente_id, calculo["subtotal"], calculo["frete"], calculo["total"],
         st.AGUARDANDO_PAGAMENTO),
    )
    pedido_id = cur.lastrowid

    for item in itens:
        conn.execute(
            "INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario, subtotal, sabor) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"],
             item["subtotal"], item["sabor"]),
        )

    conn.execute(
        "INSERT INTO pagamentos (pedido_id, tipo, valor, status) VALUES (?, 'PIX', ?, 'PENDENTE')",
        (pedido_id, calculo["total"]),
    )

    conn.execute("DELETE FROM carrinho WHERE cliente_id = ?", (cliente_id,))
    conn.commit()

    return {
        "ok": True,
        "numero_pedido": numero_pedido,
        "total": calculo["total"],
        "pix_chave": db.get_config("PIX_CHAVE"),
        "pix_nome": db.get_config("PIX_NOME"),
        "pix_banco": db.get_config("PIX_BANCO"),
    }


def consultar_pedido(cliente_id: int, numero_pedido: str = None):
    conn = db.get_conn()
    if numero_pedido:
        row = conn.execute(
            "SELECT * FROM pedidos WHERE numero_pedido = ? AND cliente_id = ?",
            (numero_pedido, cliente_id),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM pedidos WHERE cliente_id = ? ORDER BY id DESC LIMIT 1",
            (cliente_id,),
        ).fetchone()
    if not row:
        return {"erro": "pedido_nao_encontrado"}
    pedido = dict(row)
    itens = conn.execute(
        "SELECT p.nome, pi.quantidade, pi.preco_unitario, pi.sabor "
        "FROM pedido_itens pi JOIN produtos p ON p.id = pi.produto_id WHERE pi.pedido_id = ?",
        (pedido["id"],),
    ).fetchall()
    pedido["itens"] = [dict(r) for r in itens]
    return pedido


def consultar_status_pedido(numero_pedido: str):
    pedido = db.get_pedido_por_numero(numero_pedido)
    if not pedido:
        return {"erro": "pedido_nao_encontrado"}
    return {"numero_pedido": pedido["numero_pedido"], "status": pedido["status"]}


def transferir_humano(cliente_id: int, motivo: str):
    conn = db.get_conn()
    pedido = db.get_pedido_aberto(cliente_id)
    if pedido:
        conn.execute(
            "UPDATE pedidos SET status = ?, atualizado_em = datetime('now') WHERE id = ?",
            (st.HUMANO, pedido["id"]),
        )
        conn.commit()
    return {"ok": True, "transferido": True, "motivo": motivo}


# Mapa nome_da_ferramenta -> função Python correspondente.
# cliente_id é sempre injetado pelo agente (claude_agent.py), nunca vem do Claude.
FERRAMENTAS = {
    "buscar_produtos": buscar_produtos,
    "buscar_produto": buscar_produto,
    "consultar_estoque": consultar_estoque,
    "consultar_carrinho": consultar_carrinho,
    "adicionar_carrinho": adicionar_carrinho,
    "remover_carrinho": remover_carrinho,
    "calcular_carrinho": calcular_carrinho,
    "criar_pedido": criar_pedido,
    "consultar_pedido": consultar_pedido,
    "consultar_frete": consultar_frete,
    "consultar_status_pedido": consultar_status_pedido,
    "transferir_humano": transferir_humano,
}

# Ferramentas que precisam do cliente_id injetado como primeiro argumento.
FERRAMENTAS_COM_CLIENTE = {
    "consultar_carrinho", "adicionar_carrinho", "remover_carrinho", "calcular_carrinho",
    "criar_pedido", "consultar_pedido", "consultar_frete", "transferir_humano",
}
