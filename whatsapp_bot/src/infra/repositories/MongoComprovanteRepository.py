from bson import ObjectId
from pymongo.database import Database

from ...domain.entities.Comprovante import Comprovante
from ...domain.repositories.ComprovanteRepository import ComprovanteRepository


class MongoComprovanteRepository(ComprovanteRepository):
    def __init__(self, database: Database):
        self._collection = database["comprovantes"]

    def salvar(self, comprovante: Comprovante) -> Comprovante:
        documento = {
            "pedido_id": comprovante.pedido_id,
            "cliente_id": comprovante.cliente_id,
            "arquivo": comprovante.arquivo,
            "nome_arquivo": comprovante.nome_arquivo,
            "status": comprovante.status,
            "data_recebimento": comprovante.data_recebimento,
        }
        if comprovante.id:
            self._collection.update_one({"_id": ObjectId(comprovante.id)}, {"$set": documento})
        else:
            resultado = self._collection.insert_one(documento)
            comprovante.id = str(resultado.inserted_id)
        return comprovante
