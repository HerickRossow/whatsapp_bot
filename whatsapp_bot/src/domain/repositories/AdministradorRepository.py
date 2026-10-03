from abc import ABC, abstractmethod
from typing import Optional

from ..entities.Administrador import Administrador
from ..value_objects.Telefone import Telefone


class AdministradorRepository(ABC):
    @abstractmethod
    def eh_admin(self, whatsapp: Telefone) -> bool:
        ...

    @abstractmethod
    def buscar_por_whatsapp(self, whatsapp: Telefone) -> Optional[Administrador]:
        ...

    @abstractmethod
    def salvar(self, administrador: Administrador) -> Administrador:
        ...
