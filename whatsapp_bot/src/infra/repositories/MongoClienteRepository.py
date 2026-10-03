from typing import Optional

from bson import ObjectId
from pymongo.database import Database

from ...domain.entities.Cliente import Cliente
from ...domain.repositories.ClienteRepository import ClienteRepository
from ...domain.value_objects.Telefone import Telefone


class MongoClienteRepository(ClienteRepository):
    def __init__(self, database: Database):
        self._collection = database["clientes"]

    def buscar_por_whatsapp(self, whatsapp: Telefone) -> Optional[Cliente]:
        documento = self._collection.find_one({"whatsapp": whatsapp.numero})
        return self._para_entidade(documento) if documento else None

    def buscar_por_id(self, cliente_id: str) -> Optional[Cliente]:
        documento = self._collection.find_one({"_id": ObjectId(cliente_id)})
        return self._para_entidade(documento) if documento else None

    def salvar(self, cliente: Cliente) -> Cliente:
        documento = self._para_documento(cliente)
        if cliente.id:
            self._collection.update_one({"_id": ObjectId(cliente.id)}, {"$set": documento})
        else:
            resultado = self._collection.insert_one(documento)
            cliente.id = str(resultado.inserted_id)
        return cliente

    @staticmethod
    def _para_documento(cliente: Cliente) -> dict:
        return {
            "whatsapp": cliente.whatsapp.numero,
            "nome": cliente.nome,
            "cpf": cliente.cpf,
            "email": cliente.email,
            "endereco": cliente.endereco,
            "cidade": cliente.cidade,
            "cep": cliente.cep,
            "criado_em": cliente.criado_em,
            "atualizado_em": cliente.atualizado_em,
        }

    @staticmethod
    def _para_entidade(documento: dict) -> Cliente:
        return Cliente(
            id=str(documento["_id"]),
            whatsapp=Telefone(documento["whatsapp"]),
            nome=documento.get("nome"),
            cpf=documento.get("cpf"),
            email=documento.get("email"),
            endereco=documento.get("endereco"),
            cidade=documento.get("cidade"),
            cep=documento.get("cep"),
            criado_em=documento.get("criado_em"),
            atualizado_em=documento.get("atualizado_em"),
        )
