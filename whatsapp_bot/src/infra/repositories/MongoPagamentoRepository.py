from typing import Optional

from bson import ObjectId
from pymongo.database import Database

from ...domain.entities.Pagamento import Pagamento
from ...domain.enums.StatusPagamento import StatusPagamento
from ...domain.repositories.PagamentoRepository import PagamentoRepository
from ...domain.value_objects.Dinheiro import Dinheiro


class MongoPagamentoRepository(PagamentoRepository):
    def __init__(self, database: Database):
        self._collection = database["pagamentos"]

    def salvar(self, pagamento: Pagamento) -> Pagamento:
        documento = self._para_documento(pagamento)
        if pagamento.id:
            self._collection.update_one({"_id": ObjectId(pagamento.id)}, {"$set": documento})
        else:
            resultado = self._collection.insert_one(documento)
            pagamento.id = str(resultado.inserted_id)
        return pagamento

    def buscar_por_pedido(self, pedido_id: str) -> Optional[Pagamento]:
        documento = self._collection.find_one({"pedido_id": pedido_id})
        return self._para_entidade(documento) if documento else None

    @staticmethod
    def _para_documento(pagamento: Pagamento) -> dict:
        return {
            "pedido_id": pagamento.pedido_id,
            "tipo": pagamento.tipo,
            "valor": pagamento.valor.valor,
            "status": pagamento.status.value,
            "criado_em": pagamento.criado_em,
            "confirmado_em": pagamento.confirmado_em,
        }

    @staticmethod
    def _para_entidade(documento: dict) -> Pagamento:
        return Pagamento(
            id=str(documento["_id"]),
            pedido_id=documento["pedido_id"],
            tipo=documento.get("tipo", "PIX"),
            valor=Dinheiro(documento["valor"]),
            status=StatusPagamento(documento["status"]),
            criado_em=documento.get("criado_em"),
            confirmado_em=documento.get("confirmado_em"),
        )
