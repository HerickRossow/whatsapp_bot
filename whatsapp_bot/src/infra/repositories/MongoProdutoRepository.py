import re
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database

from ...domain.entities.Produto import Produto
from ...domain.repositories.ProdutoRepository import ProdutoRepository
from ...domain.value_objects.Dinheiro import Dinheiro


class MongoProdutoRepository(ProdutoRepository):
    def __init__(self, database: Database):
        self._collection = database["produtos"]

    def buscar_por_id(self, produto_id: str) -> Optional[Produto]:
        try:
            object_id = ObjectId(produto_id)
        except InvalidId:
            return None
        documento = self._collection.find_one({"_id": object_id})
        return self._para_entidade(documento) if documento else None

    def buscar_por_sku(self, sku: str) -> Optional[Produto]:
        documento = self._collection.find_one({"sku": sku})
        return self._para_entidade(documento) if documento else None

    def buscar_por_termo(self, termo: str, limite: int = 15) -> List[Produto]:
        padrao = re.compile(re.escape(termo), re.IGNORECASE)
        cursor = (
            self._collection.find(
                {
                    "ativo": True,
                    "estoque": {"$gt": 0},
                    "$or": [
                        {"nome": padrao},
                        {"marca": padrao},
                        {"categoria": padrao},
                        {"sabor": padrao},
                    ],
                }
            )
            .sort("nome")
            .limit(limite)
        )
        return [self._para_entidade(documento) for documento in cursor]

    def salvar(self, produto: Produto) -> Produto:
        documento = self._para_documento(produto)
        if produto.id:
            self._collection.update_one({"_id": ObjectId(produto.id)}, {"$set": documento})
        else:
            resultado = self._collection.insert_one(documento)
            produto.id = str(resultado.inserted_id)
        return produto

    @staticmethod
    def _para_documento(produto: Produto) -> dict:
        return {
            "sku": produto.sku,
            "nome": produto.nome,
            "marca": produto.marca,
            "categoria": produto.categoria,
            "peso": produto.peso,
            "sabor": produto.sabor,
            "preco": produto.preco.valor,
            "estoque": produto.estoque,
            "descricao": produto.descricao,
            "imagem": produto.imagem,
            "ativo": produto.ativo,
            "atualizado_em": datetime.now(),
        }

    @staticmethod
    def _para_entidade(documento: dict) -> Produto:
        return Produto(
            id=str(documento["_id"]),
            sku=documento.get("sku"),
            nome=documento["nome"],
            marca=documento.get("marca"),
            categoria=documento.get("categoria"),
            peso=documento.get("peso"),
            sabor=documento.get("sabor"),
            preco=Dinheiro(documento["preco"]),
            estoque=documento.get("estoque", 0),
            descricao=documento.get("descricao"),
            imagem=documento.get("imagem"),
            ativo=documento.get("ativo", True),
        )
