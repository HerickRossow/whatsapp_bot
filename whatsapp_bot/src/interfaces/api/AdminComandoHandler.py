import re
from typing import Optional

from ...domain.exceptions.PedidoNaoEncontradoError import PedidoNaoEncontradoError

COMANDO_RE = re.compile(
    r"^(APROVAR|RECUSAR|STATUS|PRONTO|ENVIAR|CANCELAR)\s+(\S+)(?:\s+(\S+))?$",
    re.IGNORECASE,
)


def tratar_comando_admin(container, texto: Optional[str]) -> Optional[str]:
    texto = (texto or "").strip()
    correspondencia = COMANDO_RE.match(texto)
    if not correspondencia:
        return None

    comando = correspondencia.group(1).upper()
    numero_pedido = correspondencia.group(2)
    extra = correspondencia.group(3)

    try:
        if comando == "APROVAR":
            return _aprovar(container, numero_pedido)
        if comando == "RECUSAR":
            return _recusar(container, numero_pedido)
        if comando == "STATUS":
            return _status(container, numero_pedido)
        if comando == "PRONTO":
            return _pronto(container, numero_pedido)
        if comando == "ENVIAR":
            return _enviar(container, numero_pedido, extra)
        if comando == "CANCELAR":
            return _cancelar(container, numero_pedido)
    except PedidoNaoEncontradoError:
        return f"❌ Não encontrei o pedido #{numero_pedido}."

    return None


def _aprovar(container, numero_pedido: str) -> str:
    pedido = container.confirmar_pagamento_usecase.executar(numero_pedido)
    return f"✅ Pedido #{pedido.numero_pedido} aprovado. Estoque atualizado e cliente notificado."


def _recusar(container, numero_pedido: str) -> str:
    pedido = container.recusar_pagamento_usecase.executar(numero_pedido)
    return f"🔴 Pedido #{pedido.numero_pedido} marcado como pagamento não confirmado. Cliente notificado."


def _status(container, numero_pedido: str) -> str:
    detalhes = container.obter_pedido_para_admin_usecase.executar(numero_pedido)
    if detalhes is None:
        return f"❌ Não encontrei o pedido #{numero_pedido}."
    pedido = detalhes.pedido
    linhas = "\n".join(f"{item.quantidade}x {item.nome}" for item in pedido.itens)
    nome_cliente = detalhes.cliente.nome if detalhes.cliente else "-"
    return (
        f"📋 PEDIDO #{pedido.numero_pedido}\n\n"
        f"Cliente: {nome_cliente}\n"
        f"Total: R$ {pedido.total.valor:.2f}\n\n"
        f"Status: {pedido.status.value}\n\n"
        f"Itens:\n{linhas}"
    )


def _pronto(container, numero_pedido: str) -> str:
    pedido = container.marcar_pedido_pronto_usecase.executar(numero_pedido)
    return f"📦 Pedido #{pedido.numero_pedido} marcado como pronto. Cliente notificado."


def _enviar(container, numero_pedido: str, rastreamento: Optional[str]) -> str:
    if not rastreamento:
        return "⚠️ Use: ENVIAR <numero_pedido> <codigo_rastreio>"
    pedido = container.marcar_pedido_enviado_usecase.executar(numero_pedido, rastreamento)
    return f"🚚 Pedido #{pedido.numero_pedido} marcado como enviado (rastreio {rastreamento}). Cliente notificado."


def _cancelar(container, numero_pedido: str) -> str:
    pedido = container.cancelar_pedido_usecase.executar(numero_pedido)
    return f"🚫 Pedido #{pedido.numero_pedido} cancelado. Cliente notificado."
