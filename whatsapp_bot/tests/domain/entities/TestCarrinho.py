import pytest

from src.domain.entities.Carrinho import Carrinho
from src.domain.entities.Produto import Produto
from src.domain.exceptions.CarrinhoVazioError import CarrinhoVazioError
from src.domain.exceptions.EstoqueInsuficienteError import EstoqueInsuficienteError
from src.domain.exceptions.QuantidadeInvalidaError import QuantidadeInvalidaError
from src.domain.value_objects.Dinheiro import Dinheiro


def _produto(id="p1", preco="79.90", estoque=10):
    return Produto(id=id, nome="Creatina", preco=Dinheiro(preco), estoque=estoque)


def test_adicionar_item_calcula_subtotal_correto():
    carrinho = Carrinho(cliente_id="c1")
    carrinho.adicionar_item(_produto(), 2)
    assert carrinho.subtotal.valor == 159.80


def test_adicionar_quantidade_invalida_lanca_erro():
    carrinho = Carrinho(cliente_id="c1")
    with pytest.raises(QuantidadeInvalidaError):
        carrinho.adicionar_item(_produto(), 0)


def test_adicionar_sem_estoque_suficiente_lanca_erro():
    carrinho = Carrinho(cliente_id="c1")
    with pytest.raises(EstoqueInsuficienteError):
        carrinho.adicionar_item(_produto(estoque=1), 5)


def test_remover_item_atualiza_subtotal():
    carrinho = Carrinho(cliente_id="c1")
    carrinho.adicionar_item(_produto(id="p1"), 1)
    carrinho.adicionar_item(_produto(id="p2", preco="10.00"), 1)
    carrinho.remover_item("p1")
    assert len(carrinho.itens) == 1
    assert carrinho.subtotal.valor == 10.00


def test_carrinho_vazio_exige_nao_vazio_lanca_erro():
    with pytest.raises(CarrinhoVazioError):
        Carrinho(cliente_id="c1").exigir_nao_vazio()
