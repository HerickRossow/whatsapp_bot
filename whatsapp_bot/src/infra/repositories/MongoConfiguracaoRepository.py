from typing import Optional

from pymongo.database import Database

from ...domain.repositories.ConfiguracaoRepository import ConfiguracaoRepository


class MongoConfiguracaoRepository(ConfiguracaoRepository):
    def __init__(self, database: Database):
        self._collection = database["configuracoes"]

    def obter(self, chave: str, default: Optional[str] = None) -> Optional[str]:
        documento = self._collection.find_one({"_id": chave})
        return documento["valor"] if documento else default

    def definir(self, chave: str, valor: str) -> None:
        self._collection.update_one({"_id": chave}, {"$set": {"valor": valor}}, upsert=True)
