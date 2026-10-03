import pytest

from src.domain.entities.Cliente import Cliente
from src.domain.entities.Pagamento import Pagamento
from src.domain.entities.Pedido import Pedido
from src.domain.entities.Produto import Produto
from src.domain.enums.StatusPedido import StatusPedido
from src.domain.exceptions.PedidoNaoEncontradoError import PedidoNaoEncontradoError
from src.domain.value_objects.Dinheiro import Dinheiro
from src.domain.value_objects.ItemPedido import ItemPedido
from src.domain.value_objects.Telefone import Telefone


@pytest.fixture
def pedido_aguardando_conferencia(container):
    cliente = container.cliente_repository.salvar(Cliente(whatsapp=Telefone("11988887777"), nome="Joao"))
    produto = container.produto_repository.salvar(
        Produto(nome="Creatina", preco=Dinheiro("79.90"), estoque=10, sku="CR001")
    )
    pedido = Pedido(
        numero_pedido=container.pedido_repository.proximo_numero(), cliente_id=cliente.id,
        itens=[ItemPedido(produto.id, produto.nome, 2, produto.preco)],
        subtotal=Dinheiro("159.80"), frete=Dinheiro("15.00"), total=Dinheiro("174.80"),
        status=StatusPedido.COMPROVANTE_RECEBIDO,
    )
    pedido = container.pedido_repository.salvar(pedido)
    container.pagamento_repository.salvar(Pagamento(pedido_id=pedido.id, valor=pedido.total))
    return pedido, produto


def test_confirmar_pagamento_baixa_estoque_e_notifica_cliente(container, pedido_aguardando_conferencia, whatsapp_gateway_fake):
    pedido, produto = pedido_aguardando_conferencia

    pedido_confirmado = container.confirmar_pagamento_usecase.executar(pedido.numero_pedido)

    assert pedido_confirmado.status == StatusPedido.PAGAMENTO_CONFIRMADO
    assert container.produto_repository.buscar_por_id(produto.id).estoque == 8
    assert container.pagamento_repository.buscar_por_pedido(pedido.id).status.value == "CONFIRMADO"
    assert len(whatsapp_gateway_fake.mensagens) == 1


def test_confirmar_pagamento_de_pedido_inexistente_lanca_erro(container):
    with pytest.raises(PedidoNaoEncontradoError):
        container.confirmar_pagamento_usecase.executar("999999")
