"""
Trata o recebimento de comprovantes de pagamento (imagens).
Baixa a mídia, salva em disco organizada por data, registra no SQLite,
atualiza o status do pedido e notifica o administrador.
"""
from datetime import datetime
from pathlib import Path

import config
import db
import status as st
import whatsapp_client as wa

EXT_POR_MIME = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def _nome_arquivo(pedido_numero, nome_cliente, telefone, mime_type):
    ext = EXT_POR_MIME.get(mime_type, "jpg")
    nome_limpo = (nome_cliente or "cliente").strip().replace(" ", "_")
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"PEDIDO_{pedido_numero}_{nome_limpo}_{telefone}_{agora}.{ext}"


def processar_comprovante(cliente: dict, media_id: str, mime_type: str) -> str:
    """Processa uma imagem recebida como comprovante. Retorna o texto de resposta ao cliente."""
    pedido = db.get_pedido_aberto(cliente["id"])
    if not pedido or pedido["status"] not in (st.AGUARDANDO_PAGAMENTO, st.PAGAMENTO_NAO_CONFIRMADO):
        return (
            "Recebi sua imagem, mas não encontrei um pedido aguardando pagamento no momento. "
            "Se você já fechou um pedido, me avise o número dele. 🙂"
        )

    conteudo = wa.download_media(media_id)

    hoje = datetime.now()
    pasta = Path(config.COMPROVANTES_DIR) / f"{hoje:%Y}" / f"{hoje:%m}" / f"{hoje:%d}"
    pasta.mkdir(parents=True, exist_ok=True)

    nome_arquivo = _nome_arquivo(pedido["numero_pedido"], cliente.get("nome"), cliente["whatsapp"], mime_type)
    caminho = pasta / nome_arquivo
    caminho.write_bytes(conteudo)

    conn = db.get_conn()
    conn.execute(
        "INSERT INTO comprovantes (pedido_id, cliente_id, arquivo, nome_arquivo, status) "
        "VALUES (?, ?, ?, ?, 'AGUARDANDO_CONFERENCIA')",
        (pedido["id"], cliente["id"], str(caminho), nome_arquivo),
    )
    conn.execute(
        "UPDATE pedidos SET status = ?, atualizado_em = datetime('now') WHERE id = ?",
        (st.COMPROVANTE_RECEBIDO, pedido["id"]),
    )
    conn.commit()

    _notificar_admin(cliente, pedido, str(caminho), mime_type)

    return (
        "Recebi seu comprovante! ✅ Vou encaminhar para conferência e assim que for "
        "aprovado eu te aviso por aqui. 🙌"
    )


def _notificar_admin(cliente, pedido, caminho_arquivo, mime_type):
    admin = db.get_config("ADMIN_WHATSAPP", config.ADMIN_WHATSAPP)
    if not admin:
        return

    itens = db.get_conn().execute(
        "SELECT p.nome, pi.quantidade FROM pedido_itens pi "
        "JOIN produtos p ON p.id = pi.produto_id WHERE pi.pedido_id = ?",
        (pedido["id"],),
    ).fetchall()
    linhas_itens = "\n".join(f"{i['quantidade']}x {i['nome']}" for i in itens)

    texto = (
        "🚨 NOVO COMPROVANTE DE PAGAMENTO\n\n"
        f"📋 Pedido: #{pedido['numero_pedido']}\n\n"
        f"👤 Cliente: {cliente.get('nome') or 'não informado'}\n"
        f"📱 WhatsApp: {cliente['whatsapp']}\n\n"
        f"🛒 PEDIDO:\n{linhas_itens}\n\n"
        f"💰 TOTAL: R$ {pedido['total']:.2f}\n"
        "💳 PAGAMENTO: PIX\n"
        "⚠️ STATUS: AGUARDANDO CONFERÊNCIA\n\n"
        f"Responda: APROVAR {pedido['numero_pedido']} ou RECUSAR {pedido['numero_pedido']}"
    )

    try:
        wa.send_text(admin, texto)
        wa.send_image_by_path(admin, caminho_arquivo, mime_type=mime_type or "image/jpeg")
    except Exception as e:
        db.registrar_erro("media_handler", pedido["numero_pedido"], str(e))
