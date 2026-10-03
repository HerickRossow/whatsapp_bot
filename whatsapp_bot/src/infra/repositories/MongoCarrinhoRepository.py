from pymongo.database import Database

from ...domain.entities.Carrinho import Carrinho
from ...domain.repositories.CarrinhoRepository import CarrinhoRepository
from ...domain.value_objects.Dinheiro import Dinheiro
from ...domain.value_objects.ItemCarrinho import ItemCarrinho


class MongoCarrinhoRepository(CarrinhoRepository):
    def __init__(self, database: Database):
        self._collection = database["carrinhos"]

    def buscar_por_cliente(self, cliente_id: str) -> Carrinho:
        documento = self._collection.find_one({"cliente_id": cliente_id})
        if not documento:
            return Carrinho(cliente_id=cliente_id)
        itens = [
            ItemCarrinho(
                produto_id=item["produto_id"],
                nome=item["nome"],
                quantidade=item["quantidade"],
                preco_unitario=Dinheiro(item["preco_unitario"]),
                sabor=item.get("sabor"),
            )
            for item in documento.get("itens", [])
        ]
        return Carrinho(cliente_id=cliente_id, itens=itens)

    def salvar(self, carrinho: Carrinho) -> None:
        itens = [
            {
                "produto_id": item.produto_id,
                "nome": item.nome,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario.valor,
                "sabor": item.sabor,
            }
            for item in carrinho.itens
        ]
        self._collection.update_one(
            {"cliente_id": carrinho.cliente_id},
            {"$set": {"itens": itens}},
            upsert=True,
        )

    def limpar(self, cliente_id: str) -> None:
        self._collection.delete_one({"cliente_id": cliente_id})
