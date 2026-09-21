# ==========================================
# 1. BIBLIOTECAS
# ==========================================
# from math import integer
from pydantic import BaseModel, Field
from typing import Optional, List

# from model.produto import Produto
# from model.estabelecimento import Estabelecimento
from model.constants import *

from schemas.estabelecimento import EstabelecimentoSchema

from datetime import datetime

from pydantic import BaseModel
from typing import List


class ProdutoDaLista(BaseModel):
    nome: str = "Leite Zero Ninho 1L"
    marca: str = "Ninho"
    preco_medio: float = 11.99
    quantidade: int = 2


class ListaDeComprasSchema(BaseModel):
    titulo: str = "João Pessoa com Matheus"
    itens: List[ProdutoDaLista]


class BuscarListaDeCompras(BaseModel):
    titulo: str = "João Pessoa com Matheus"


class ProdutoAdicionadoNaLista(BaseModel):
    message: str
    addedQuantity: int
    quantityNotAdded: int


# ==========================================
# 2. MODELOS DE REQUISIÇÃO
# ==========================================


class CriarListaDeComprasSchema(BaseModel):
    titulo: str = "João Pessoa com Matheus"


class NomeDosItens(BaseModel):
    nome: str = "Leite Zero Ninho 1L"


class ApagarItemDaLista(BaseModel):
    titulo: str = "João Pessoa com Matheus"
    itens: List[NomeDosItens]


# ==========================================
# 3. MODELOS DE RESPOSTA
# ==========================================


class ListReplySchema(BaseModel):
    message: str


class ListErrorSchema(BaseModel):
    message: str
    
class AddListReplySchema(BaseModel):
    message: str
    addedQuantity: int
    quantityNotAdded: int
