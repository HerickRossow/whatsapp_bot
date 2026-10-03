import pytest

from src.domain.value_objects.Telefone import Telefone


def test_normaliza_numero_com_formatacao():
    assert Telefone("55 (11) 98888-7777").numero == "5511988887777"


def test_numero_muito_curto_e_invalido():
    with pytest.raises(ValueError):
        Telefone("12345")


def test_telefones_com_mesmo_numero_sao_iguais():
    assert Telefone("11988887777") == Telefone("(11) 98888-7777")
