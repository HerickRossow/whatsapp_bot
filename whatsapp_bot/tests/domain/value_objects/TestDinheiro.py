from src.domain.value_objects.Dinheiro import Dinheiro


def test_arredonda_para_duas_casas_decimais():
    assert Dinheiro("79.905").valor == 79.91


def test_soma_dois_valores():
    assert (Dinheiro("10.50") + Dinheiro("5.25")).valor == 15.75


def test_multiplica_por_quantidade():
    assert (Dinheiro("9.99") * 3).valor == 29.97


def test_valores_iguais_sao_iguais():
    assert Dinheiro("10.00") == Dinheiro(10)


def test_comparacao_menor_que():
    assert Dinheiro("5.00") < Dinheiro("10.00")
