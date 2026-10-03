from ...domain.entities.Cliente import Cliente
from ...domain.repositories.ClienteRepository import ClienteRepository
from ...domain.value_objects.Telefone import Telefone


class ObterOuCriarClienteUseCase:
    def __init__(self, cliente_repository: ClienteRepository):
        self._cliente_repository = cliente_repository

    def executar(self, whatsapp: str, nome: str = None) -> Cliente:
        telefone = Telefone(whatsapp)
        cliente = self._cliente_repository.buscar_por_whatsapp(telefone)
        if cliente is None:
            return self._cliente_repository.salvar(Cliente(whatsapp=telefone, nome=nome))

        nome_anterior = cliente.nome
        cliente.atualizar_nome(nome)
        if cliente.nome != nome_anterior:
            self._cliente_repository.salvar(cliente)
        return cliente
