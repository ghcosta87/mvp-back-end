from sqlalchemy import Column, Float, ForeignKey, String, Integer, DateTime, Date, Float

# from sqlalchemy.orm import relationship # para usar JOIN
from datetime import datetime
from typing import Union
from model import Base  # , Estabelecimento  # , Comentario


class Produto(Base):
    __tablename__ = "produtos"

    id = Column("pk_produto", Integer, primary_key=True)
    nome = Column(String(100), unique=True)
    marca = Column(String(200))
    preco = Column(Float)
    # estabelecimento = Column(Integer, ForeignKey("estabelecimentos.pk_estabelecimento"))
    # a verificar interligação entre as tabelas produto e estabelecimento
    data_de_cadastro = Column(DateTime, default=datetime.now())

    def __init__(
        self, id: int, nome: str, marca: str, preco: float
    ):  # , estabelecimento: int):
        """
        Cadastra um novo produto no banco de dados
        id: id do produto
        nome: nome do produto
        marca: marca do produto
        preco: preco do produto
        estabelecimento: id do estabelecimento que vende o produto
        data_de_cadastro:  data de cadastro do produto
        """
        self.id = id
        self.nome = nome
        self.marca = marca
        self.preco = preco
        # self.estabelecimento = estabelecimento
        self.data_de_cadastro = datetime.now()
