from typing import Optional

from pymongo.database import Database

from ...domain.entities.Administrador import Administrador
from ...domain.repositories.AdministradorRepository import AdministradorRepository
from ...domain.value_objects.Telefone import Telefone


class MongoAdministradorRepository(AdministradorRepository):
    def __init__(self, database: Database):
        self._collection = database["administradores"]

    def eh_admin(self, whatsapp: Telefone) -> bool:
        return self._collection.find_one({"whatsapp": whatsapp.numero, "ativo": True}) is not None

    def buscar_por_whatsapp(self, whatsapp: Telefone) -> Optional[Administrador]:
        documento = self._collection.find_one({"whatsapp": whatsapp.numero})
        return self._para_entidade(documento) if documento else None

    def salvar(self, administrador: Administrador) -> Administrador:
        documento = {
            "whatsapp": administrador.whatsapp.numero,
            "nome": administrador.nome,
            "ativo": administrador.ativo,
        }
        self._collection.update_one(
            {"whatsapp": administrador.whatsapp.numero},
            {"$set": documento},
            upsert=True,
        )
        if administrador.id is None:
            documento_salvo = self._collection.find_one({"whatsapp": administrador.whatsapp.numero})
            administrador.id = str(documento_salvo["_id"])
        return administrador

    @staticmethod
    def _para_entidade(documento: dict) -> Administrador:
        return Administrador(
            id=str(documento["_id"]),
            whatsapp=Telefone(documento["whatsapp"]),
            nome=documento.get("nome"),
            ativo=documento.get("ativo", True),
        )
