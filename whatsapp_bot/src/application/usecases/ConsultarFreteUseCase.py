from ...domain.repositories.ConfiguracaoRepository import ConfiguracaoRepository
from ...domain.value_objects.Dinheiro import Dinheiro


class ConsultarFreteUseCase:
    def __init__(self, configuracao_repository: ConfiguracaoRepository, frete_padrao: Dinheiro):
        self._configuracao_repository = configuracao_repository
        self._frete_padrao = frete_padrao

    def executar(self) -> Dinheiro:
        valor_configurado = self._configuracao_repository.obter("FRETE_PADRAO")
        if valor_configurado is None:
            return self._frete_padrao
        return Dinheiro(valor_configurado)
