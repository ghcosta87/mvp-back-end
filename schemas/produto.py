from pydantic import BaseModel, Field
from typing import Optional, List

# from model.produto import Produto
# from model.estabelecimento import Estabelecimento
from model.constants import *

from schemas.estabelecimento import EstabelecimentoSchema

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
    """Define como um novo produto a ser inserido deve ser representado"""

    nome: str = "Leite Zero Lactose"
    marca: str = "Parmalat"
    preco: float = 9.99
    data_da_compra: datetime = Field(default_factory=datetime.now)
    # estabelecimento: int = 1
    # data_de_cadastro = datetime.now()
    data_de_cadastro: datetime = Field(default_factory=datetime.now)


class ProdutoItemSchema(BaseModel):
    id: int
    nome: str
    data_da_compra: datetime
    preco: float


class EstatisticaSchema(BaseModel):
    nome: str
    total_compras: int
    preco_medio: float
    menor_preco: float
    maior_preco: float


class HistoricoItemSchema(BaseModel):
    data: datetime
    valor: float


class ConsultaSchema(BaseModel):
    produtos: List[ProdutoItemSchema]
    estatisticas: List[EstatisticaSchema]
    historico: dict[str, List[HistoricoItemSchema]]


class ProductNotFoundSchema(BaseModel):
    message: str
    product_name: str


class ProductUpdateReplySchema(BaseModel):
    nome_antigo: str = "Leite Zero Lactose"
    nome: str = "Leite Zero Lactose 1L"
    marca: str = "Parmalat"
    preco: float = 9.99
    data_da_compra: datetime = Field(default_factory=datetime.now)
    message: str = "Mensagem de edição com sucesso"

class ProductReplySchema(BaseModel):
    """Define como um novo produto a ser inserido deve ser representado"""

    nome: str
    marca: str
    preco: float
    data_da_compra: datetime 
    data_de_cadastro: datetime = Field(default_factory=datetime.now)
    message: str