from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

from ..config.Settings import settings

_client: Optional[MongoClient] = None


def obter_cliente() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri)
    return _client


def obter_database() -> Database:
    return obter_cliente()[settings.mongo_db_name]


def criar_indices(database: Database) -> None:
    database["clientes"].create_index("whatsapp", unique=True)
    database["administradores"].create_index("whatsapp", unique=True)
    database["pedidos"].create_index("numero_pedido", unique=True)
    database["carrinhos"].create_index("cliente_id", unique=True)
    database["produtos"].create_index("sku")
