from typing import List

from pymongo.database import Database

from ...domain.entities.Conversa import Conversa
from ...domain.repositories.ConversaRepository import ConversaRepository


class MongoConversaRepository(ConversaRepository):
    def __init__(self, database: Database):
        self._collection = database["conversas"]

    def salvar(self, conversa: Conversa) -> None:
        self._collection.insert_one(
            {
                "cliente_id": conversa.cliente_id,
                "tipo": conversa.tipo,
                "mensagem": conversa.mensagem,
                "origem": conversa.origem,
                "criado_em": conversa.criado_em,
            }
        )

    def buscar_historico(self, cliente_id: str, limite: int = 20) -> List[Conversa]:
        cursor = self._collection.find({"cliente_id": cliente_id}).sort("_id", -1).limit(limite)
        conversas = [
            Conversa(
                id=str(documento["_id"]),
                cliente_id=documento["cliente_id"],
                tipo=documento["tipo"],
                mensagem=documento["mensagem"],
                origem=documento["origem"],
                criado_em=documento.get("criado_em"),
            )
            for documento in cursor
        ]
        return list(reversed(conversas))
