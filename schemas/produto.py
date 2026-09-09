from pydantic import BaseModel, Field
from typing import Optional, List

from model.produto import Produto
from model.estabelecimento import Estabelecimento
from model.constants import *

from schemas.estabelecimento import EstabelecimentoSchema

# from model import Session  # Importa a sessão do SQLAlchemy

from datetime import datetime

from pydantic import BaseModel
from typing import List


class ItemExtraido(BaseModel):
    """Representa um único produto lido da nota fiscal"""

    nome: str
    # descricao: str
    marca: str
    loja: str
    preco: float

class CupomExtraidoSchema(BaseModel):
    """Representa o resultado total que a IA vai devolver"""

    loja: EstabelecimentoSchema
    # nome_da_loja: str
    # descricao_da_loja: str
    # endereco_da_loja: str
    # marca: str
    data: datetime = Field(default_factory=datetime.now)
    produtos: List[ItemExtraido]


class ProdutoSchema(BaseModel):
    """Define como um novo usuário a ser inserido deve ser representado"""

    nome: str = "Leite Zero Lactose"
    marca: str = "Parmalat"
    preco: float = 9.99
    data_da_compra: datetime = Field(default_factory=datetime.now)
    # estabelecimento: int = 1
    # data_de_cadastro = datetime.now()
    data_de_cadastro: datetime = Field(default_factory=datetime.now)


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

# from sqlalchemy import func

# def listar_produtos_agrupados(session):
#     subquery = (
#         session.query(
#             Produto.nome,
#             func.max(Produto.data_da_compra).label("ultima_data")
#         )
#         .group_by(Produto.nome)
#         .subquery()
#     )

#     produtos_atuais = (
#         session.query(Produto)
#         .join(
#             subquery,
#             (Produto.nome == subquery.c.nome) &
#             (Produto.data_da_compra == subquery.c.ultima_data)
#         )
#         .all()
#     )

#     return produtos_atuais