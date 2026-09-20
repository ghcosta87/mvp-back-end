from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Float
from typing import Optional, List
from datetime import datetime
from model import Base  # , Comentario
from sqlalchemy.orm import relationship


class ListaDeCompras(Base):
    __tablename__ = "lista_de_compras"

    id = Column("pk_lista", Integer, primary_key=True)
    titulo = Column(String,primary_key=True)

    itens = relationship(
        "ListaDeItens", back_populates="lista", cascade="all, delete-orphan"
    )
    # cascade="all, delete-orphan" →
    # back_populates="lista" → garante que duas classes estão conectadas

    def __ini__(self, titulo: str):
        """
        Cadastra um novo produto no banco de dados
        id: id do produto
        nome: nome do produto
        """
        self.titulo = titulo


class ListaDeItens(Base):
    __tablename__ = "lista_de_itens"

    id = Column("pk_item", Integer, primary_key=True)
    quantidade = Column(Integer)

    lista_id = Column(Integer, ForeignKey("lista_de_compras.pk_lista"))

    lista = relationship("ListaDeCompras", back_populates="itens")

    produto_id = Column(Integer, ForeignKey("produtos.pk_produto"))

    produto = relationship("Produto")