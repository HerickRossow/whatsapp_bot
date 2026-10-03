import pytest

from src.domain.entities.Pedido import Pedido
from src.domain.enums.StatusPedido import StatusPedido
from src.domain.exceptions.TransicaoInvalidaError import TransicaoInvalidaError
from src.domain.value_objects.Dinheiro import Dinheiro


def _pedido(status=StatusPedido.AGUARDANDO_PAGAMENTO):
    return Pedido(
        numero_pedido="000001", cliente_id="c1", itens=[],
        subtotal=Dinheiro("100.00"), frete=Dinheiro("15.00"), total=Dinheiro("115.00"), status=status,
    )


def test_confirmar_pagamento_a_partir_de_comprovante_recebido():
    pedido = _pedido(status=StatusPedido.COMPROVANTE_RECEBIDO)
    pedido.confirmar_pagamento()
    assert pedido.status == StatusPedido.PAGAMENTO_CONFIRMADO


def test_confirmar_pagamento_em_status_invalido_lanca_erro():
    pedido = _pedido(status=StatusPedido.NOVO)
    with pytest.raises(TransicaoInvalidaError):
        pedido.confirmar_pagamento()


def test_enviar_sem_codigo_de_rastreio_lanca_erro():
    pedido = _pedido(status=StatusPedido.PRONTO)
    with pytest.raises(ValueError):
        pedido.enviar("")


def test_enviar_com_codigo_atualiza_status_e_rastreamento():
    pedido = _pedido(status=StatusPedido.PRONTO)
    pedido.enviar("BR123456789")
    assert pedido.status == StatusPedido.ENVIADO
    assert pedido.rastreamento == "BR123456789"


def test_status_abertos_nao_incluem_enviado_finalizado_cancelado():
    assert StatusPedido.ENVIADO.esta_aberto is False
    assert StatusPedido.FINALIZADO.esta_aberto is False
    assert StatusPedido.CANCELADO.esta_aberto is False
    assert StatusPedido.AGUARDANDO_PAGAMENTO.esta_aberto is True
