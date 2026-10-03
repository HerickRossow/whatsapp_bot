"""
Comandos que o número administrativo pode enviar pelo WhatsApp para
gerenciar pedidos: APROVAR, RECUSAR, STATUS, PRONTO, ENVIAR, CANCELAR.

Segurança: handle_admin_message só deve ser chamado depois que db.is_admin()
confirmar que o remetente é um administrador ativo.
"""
import re

import db
import status as st
import whatsapp_client as wa

COMANDO_RE = re.compile(
    r"^(APROVAR|RECUSAR|STATUS|PRONTO|ENVIAR|CANCELAR)\s+(\S+)(?:\s+(\S+))?$",
    re.IGNORECASE,
)


def handle_admin_message(texto: str) -> str:
    texto = (texto or "").strip()
    m = COMANDO_RE.match(texto)
    if not m:
        return None  # não é um comando reconhecido; deixa seguir fluxo normal

    comando = m.group(1).upper()
    numero_pedido = m.group(2)
    extra = m.group(3)

    if comando == "APROVAR":
        return _aprovar(numero_pedido)
    if comando == "RECUSAR":
        return _recusar(numero_pedido)
    if comando == "STATUS":
        return _status(numero_pedido)
    if comando == "PRONTO":
        return _pronto(numero_pedido)
    if comando == "ENVIAR":
        return _enviar(numero_pedido, extra)
    if comando == "CANCELAR":
        return _cancelar(numero_pedido)
    return None


def _get_pedido_ou_erro(numero_pedido):
    pedido = db.get_pedido_por_numero(numero_pedido)
    if not pedido:
        return None, f"❌ Não encontrei o pedido #{numero_pedido}."
    return pedido, None


def _cliente_whatsapp(cliente_id):
    conn = db.get_conn()
    row = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
    return dict(row) if row else None


def _aprovar(numero_pedido):
    pedido, erro = _get_pedido_ou_erro(numero_pedido)
    if erro:
        return erro
    if pedido["status"] not in (st.COMPROVANTE_RECEBIDO, st.AGUARDANDO_CONFERENCIA):
        return f"⚠️ Pedido #{numero_pedido} não está aguardando conferência (status atual: {pedido['status']})."

    conn = db.get_conn()
    try:
        conn.execute("BEGIN")
        conn.execute(
            "UPDATE pagamentos SET status = 'CONFIRMADO', confirmado_em = datetime('now') "
            "WHERE pedido_id = ?",
            (pedido["id"],),
        )
        conn.execute(
            "UPDATE pedidos SET status = ?, atualizado_em = datetime('now') WHERE id = ?",
            (st.PAGAMENTO_CONFIRMADO, pedido["id"]),
        )
        itens = conn.execute(
            "SELECT produto_id, quantidade FROM pedido_itens WHERE pedido_id = ?", (pedido["id"],)
        ).fetchall()
        for item in itens:
            conn.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (item["quantidade"], item["produto_id"], item["quantidade"]),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    cliente = _cliente_whatsapp(pedido["cliente_id"])
    if cliente:
        wa.send_text(
            cliente["whatsapp"],
            f"✅ Pagamento confirmado!\n\nSeu pedido #{numero_pedido} foi aprovado.\n\n"
            "Estamos separando seus produtos. 👊\n\nAssim que estiver pronto para envio, avisaremos você.",
        )
    return f"✅ Pedido #{numero_pedido} aprovado. Estoque atualizado e cliente notificado."


def _recusar(numero_pedido):
    pedido, erro = _get_pedido_ou_erro(numero_pedido)
    if erro:
        return erro

    conn = db.get_conn()
    conn.execute(
        "UPDATE pagamentos SET status = 'RECUSADO' WHERE pedido_id = ?", (pedido["id"],)
    )
    conn.execute(
        "UPDATE pedidos SET status = ?, atualizado_em = datetime('now') WHERE id = ?",
        (st.PAGAMENTO_NAO_CONFIRMADO, pedido["id"]),
    )
    conn.commit()

    cliente = _cliente_whatsapp(pedido["cliente_id"])
    if cliente:
        wa.send_text(
            cliente["whatsapp"],
            "Oi! Verificamos o comprovante, mas o pagamento ainda não pôde ser confirmado.\n\n"
            "Por favor, confira os dados do PIX e, se necessário, envie um novo comprovante. 👍",
        )
    return f"🔴 Pedido #{numero_pedido} marcado como pagamento não confirmado. Cliente notificado."


def _status(numero_pedido):
    pedido, erro = _get_pedido_ou_erro(numero_pedido)
    if erro:
        return erro
    conn = db.get_conn()
    cliente = _cliente_whatsapp(pedido["cliente_id"])
    itens = conn.execute(
        "SELECT p.nome, pi.quantidade FROM pedido_itens pi JOIN produtos p ON p.id = pi.produto_id "
        "WHERE pi.pedido_id = ?",
        (pedido["id"],),
    ).fetchall()
    linhas = "\n".join(f"{i['quantidade']}x {i['nome']}" for i in itens)
    return (
        f"📋 PEDIDO #{numero_pedido}\n\n"
        f"Cliente: {cliente['nome'] if cliente else '-'}\n"
        f"Total: R$ {pedido['total']:.2f}\n\n"
        f"Status: {pedido['status']}\n\n"
        f"Itens:\n{linhas}"
    )


def _pronto(numero_pedido):
    pedido, erro = _get_pedido_ou_erro(numero_pedido)
    if erro:
        return erro
    conn = db.get_conn()
    conn.execute(
        "UPDATE pedidos SET status = ?, atualizado_em = datetime('now') WHERE id = ?",
        (st.PRONTO, pedido["id"]),
    )
    conn.commit()
    cliente = _cliente_whatsapp(pedido["cliente_id"])
    if cliente:
        wa.send_text(
            cliente["whatsapp"],
            f"📦 Pedido #{numero_pedido} pronto!\n\nSeu pedido já está separado e disponível para envio/retirada.",
        )
    return f"📦 Pedido #{numero_pedido} marcado como pronto. Cliente notificado."


def _enviar(numero_pedido, rastreamento):
    pedido, erro = _get_pedido_ou_erro(numero_pedido)
    if erro:
        return erro
    if not rastreamento:
        return "⚠️ Use: ENVIAR <numero_pedido> <codigo_rastreio>"
    conn = db.get_conn()
    conn.execute(
        "UPDATE pedidos SET status = ?, rastreamento = ?, atualizado_em = datetime('now') WHERE id = ?",
        (st.ENVIADO, rastreamento, pedido["id"]),
    )
    conn.commit()
    cliente = _cliente_whatsapp(pedido["cliente_id"])
    if cliente:
        wa.send_text(
            cliente["whatsapp"],
            f"🚚 Seu pedido #{numero_pedido} foi enviado!\n\n📦 Código de rastreio:\n{rastreamento}",
        )
    return f"🚚 Pedido #{numero_pedido} marcado como enviado (rastreio {rastreamento}). Cliente notificado."


def _cancelar(numero_pedido):
    pedido, erro = _get_pedido_ou_erro(numero_pedido)
    if erro:
        return erro
    conn = db.get_conn()
    conn.execute(
        "UPDATE pedidos SET status = ?, atualizado_em = datetime('now') WHERE id = ?",
        (st.CANCELADO, pedido["id"]),
    )
    conn.commit()
    cliente = _cliente_whatsapp(pedido["cliente_id"])
    if cliente:
        wa.send_text(cliente["whatsapp"], f"Seu pedido #{numero_pedido} foi cancelado.")
    return f"🚫 Pedido #{numero_pedido} cancelado. Cliente notificado."
