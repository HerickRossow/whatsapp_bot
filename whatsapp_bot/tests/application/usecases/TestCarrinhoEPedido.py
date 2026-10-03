import pytest

from src.domain.entities.Produto import Produto
from src.domain.exceptions.CarrinhoVazioError import CarrinhoVazioError
from src.domain.exceptions.EstoqueInsuficienteError import EstoqueInsuficienteError
from src.domain.exceptions.ProdutoNaoEncontradoError import ProdutoNaoEncontradoError
from src.domain.value_objects.Dinheiro import Dinheiro


@pytest.fixture
def creatina(container):
    return container.produto_repository.salvar(Produto(nome="Creatina", preco=Dinheiro("79.90"), estoque=10, sku="CR001"))


def test_adicionar_produto_inexistente_lanca_erro(container):
    with pytest.raises(ProdutoNaoEncontradoError):
        container.adicionar_item_carrinho_usecase.executar("cliente-1", "000000000000000000000000", 1)


def test_adicionar_produto_com_id_mal_formado_lanca_erro_de_dominio(container):
    # regressão: MongoProdutoRepository.buscar_por_id estourava bson.errors.InvalidId
    # em vez de devolver None para um id que não é um ObjectId válido (achado na PR6)
    with pytest.raises(ProdutoNaoEncontradoError):
        container.adicionar_item_carrinho_usecase.executar("cliente-1", "id-nao-e-um-objectid", 1)


def test_adicionar_sem_estoque_suficiente_lanca_erro(container, creatina):
    with pytest.raises(EstoqueInsuficienteError):
        container.adicionar_item_carrinho_usecase.executar("cliente-1", creatina.id, 20)


def test_criar_pedido_com_carrinho_vazio_lanca_erro(container):
    with pytest.raises(CarrinhoVazioError):
        container.criar_pedido_usecase.executar("cliente-1")


def test_fluxo_completo_carrinho_ate_pedido(container, creatina):
    cliente_id = "cliente-1"
    container.adicionar_item_carrinho_usecase.executar(cliente_id, creatina.id, 2)

    resumo = container.calcular_carrinho_usecase.executar(cliente_id)
    assert resumo.subtotal.valor == 159.80
    assert resumo.total.valor == 174.80

    pedido = container.criar_pedido_usecase.executar(cliente_id)
    assert pedido.numero_pedido == "000001"
    assert pedido.total.valor == 174.80
    assert container.consultar_carrinho_usecase.executar(cliente_id).esta_vazio

    pagamento = container.pagamento_repository.buscar_por_pedido(pedido.id)
    assert pagamento.valor.valor == 174.80


def test_consultar_pedido_valida_posse_do_cliente(container, creatina):
    container.adicionar_item_carrinho_usecase.executar("cliente-dono", creatina.id, 1)
    pedido = container.criar_pedido_usecase.executar("cliente-dono")

    assert container.consultar_pedido_usecase.executar("cliente-dono", pedido.numero_pedido) is not None
    assert container.consultar_pedido_usecase.executar("outro-cliente", pedido.numero_pedido) is None
