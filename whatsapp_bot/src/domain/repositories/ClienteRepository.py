from abc import ABC, abstractmethod
from typing import Optional

from ..entities.Cliente import Cliente
from ..value_objects.Telefone import Telefone


class ClienteRepository(ABC):
    @abstractmethod
    def buscar_por_whatsapp(self, whatsapp: Telefone) -> Optional[Cliente]:
        ...

    @abstractmethod
    def buscar_por_id(self, cliente_id: str) -> Optional[Cliente]:
        ...

    @abstractmethod
    def salvar(self, cliente: Cliente) -> Cliente:
        ...
