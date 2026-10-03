import pytest

from src.domain.entities.Produto import Produto
from src.domain.exceptions.EstoqueInsuficienteError import EstoqueInsuficienteError
from src.domain.value_objects.Dinheiro import Dinheiro


def _produto(estoque=10, ativo=True):
    return Produto(nome="Creatina", preco=Dinheiro("79.90"), estoque=estoque, ativo=ativo)


def test_disponivel_quando_ativo_e_com_estoque():
    assert _produto(estoque=5).esta_disponivel(3) is True


def test_indisponivel_quando_inativo():
    assert _produto(ativo=False).esta_disponivel(1) is False


def test_indisponivel_quando_estoque_insuficiente():
    assert _produto(estoque=2).esta_disponivel(3) is False


def test_baixar_estoque_reduz_quantidade():
    produto = _produto(estoque=10)
    produto.baixar_estoque(4)
    assert produto.estoque == 6


def test_baixar_estoque_insuficiente_lanca_erro():
    produto = _produto(estoque=2)
    with pytest.raises(EstoqueInsuficienteError):
        produto.baixar_estoque(3)
