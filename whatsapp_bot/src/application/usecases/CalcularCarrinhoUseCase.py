from ...domain.repositories.CarrinhoRepository import CarrinhoRepository
from ..dto.ResumoCarrinho import ResumoCarrinho
from .ConsultarFreteUseCase import ConsultarFreteUseCase


class CalcularCarrinhoUseCase:
    def __init__(self, carrinho_repository: CarrinhoRepository, consultar_frete_usecase: ConsultarFreteUseCase):
        self._carrinho_repository = carrinho_repository
        self._consultar_frete_usecase = consultar_frete_usecase

    def executar(self, cliente_id: str) -> ResumoCarrinho:
        carrinho = self._carrinho_repository.buscar_por_cliente(cliente_id)
        frete = self._consultar_frete_usecase.executar()
        subtotal = carrinho.subtotal
        return ResumoCarrinho(itens=carrinho.itens, subtotal=subtotal, frete=frete, total=subtotal + frete)
