from pydantic import BaseModel, Field
from typing import Optional, List

from model.produto import Produto
from model.constants import *
# from model import Session  # Importa a sessão do SQLAlchemy

from datetime import datetime

from pydantic import BaseModel
from typing import List


class ItemExtraido(BaseModel):
    """Representa um único produto lido da nota fiscal"""
    nome: str
    # descricao: str
    marca: str
    preco: float

class CupomExtraidoSchema(BaseModel):
    """Representa o resultado total que a IA vai devolver"""
    estabelecimento: str
    marca: str
    data: str
    produtos: List[ItemExtraido]

class ProdutoSchema(BaseModel):
    """Define como um novo usuário a ser inserido deve ser representado"""
    nome: str = "Leite Zero Lactose"
    marca: str = "Parmalat"
    preco: float = 9.99
    # estabelecimento: int = 1
    # data_de_cadastro = datetime.now()
    data_de_cadastro: datetime = Field(
        default_factory=datetime.now
    )  # <--- Tipo (: datetime) e Field adicionados

# class ProdutoBuscaSchema(BaseModel):
#     """Define como deve ser a estrutura que representa a busca. Que será
#     feita apenas com base no nome do usuário.
#     """

#     nome: str = "Leite Zero Lactose"


# class ListagemProdutosSchema(BaseModel):
#     """Define como uma listagem de usuários será retornada."""

#     nome: List[ProdutoSchema]


# def apresenta_produto(produto: ProdutoSchema):
#     """Retorna uma representação do produto seguindo o schema definido em
#     UsuarioViewSchema.
#     """
#     return {
#         "nome": produto.nome,
#         "marca": produto.marca,
#         "preco": produto.preco,
#         # "estabelecimento": produto.estabelecimento,
#         "data_de_cadastro": produto.data_de_cadastro.isoformat(),
#     }


# def adicionar_produto(produto: Produto):
#     """Adiciona um produto no banco de dados"""
#     session = Session()
#     session.add(produto)
#     session.commit()