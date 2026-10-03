from typing import List, Optional

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from ...domain.entities.Pedido import Pedido
from ...domain.enums.StatusPedido import StatusPedido
from ...domain.repositories.PedidoRepository import PedidoRepository
from ...domain.value_objects.Dinheiro import Dinheiro
from ...domain.value_objects.ItemPedido import ItemPedido


class MongoPedidoRepository(PedidoRepository):
    def __init__(self, database: Database):
        self._collection = database["pedidos"]
        self._contadores = database["contadores"]

    def proximo_numero(self) -> str:
        contador = self._contadores.find_one_and_update(
            {"_id": "numero_pedido"},
            {"$inc": {"valor": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return f"{contador['valor']:06d}"

    def salvar(self, pedido: Pedido) -> Pedido:
        documento = self._para_documento(pedido)
        if pedido.id:
            self._collection.update_one({"_id": ObjectId(pedido.id)}, {"$set": documento})
        else:
            resultado = self._collection.insert_one(documento)
            pedido.id = str(resultado.inserted_id)
        return pedido

    def buscar_por_numero(self, numero_pedido: str) -> Optional[Pedido]:
        documento = self._collection.find_one({"numero_pedido": numero_pedido})
        return self._para_entidade(documento) if documento else None

    def buscar_aberto_por_cliente(self, cliente_id: str) -> Optional[Pedido]:
        status_abertos = [status.value for status in StatusPedido if status.esta_aberto]
        documento = self._collection.find_one(
            {"cliente_id": cliente_id, "status": {"$in": status_abertos}},
            sort=[("_id", -1)],
        )
        return self._para_entidade(documento) if documento else None

    @staticmethod
    def _para_documento(pedido: Pedido) -> dict:
        return {
            "numero_pedido": pedido.numero_pedido,
            "cliente_id": pedido.cliente_id,
            "itens": [
                {
                    "produto_id": item.produto_id,
                    "nome": item.nome,
                    "quantidade": item.quantidade,
                    "preco_unitario": item.preco_unitario.valor,
                    "sabor": item.sabor,
                }
                for item in pedido.itens
            ],
            "subtotal": pedido.subtotal.valor,
            "frete": pedido.frete.valor,
            "total": pedido.total.valor,
            "status": pedido.status.value,
            "rastreamento": pedido.rastreamento,
            "criado_em": pedido.criado_em,
            "atualizado_em": pedido.atualizado_em,
        }

    @staticmethod
    def _para_entidade(documento: dict) -> Pedido:
        itens = [
            ItemPedido(
                produto_id=item["produto_id"],
                nome=item["nome"],
                quantidade=item["quantidade"],
                preco_unitario=Dinheiro(item["preco_unitario"]),
                sabor=item.get("sabor"),
            )
            for item in documento.get("itens", [])
        ]
        return Pedido(
            id=str(documento["_id"]),
            numero_pedido=documento["numero_pedido"],
            cliente_id=documento["cliente_id"],
            itens=itens,
            subtotal=Dinheiro(documento["subtotal"]),
            frete=Dinheiro(documento["frete"]),
            total=Dinheiro(documento["total"]),
            status=StatusPedido(documento["status"]),
            rastreamento=documento.get("rastreamento"),
            criado_em=documento.get("criado_em"),
            atualizado_em=documento.get("atualizado_em"),
        )
