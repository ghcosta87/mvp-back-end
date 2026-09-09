from sqlalchemy import Column, Float, String, Integer, DateTime, Date #,Float

# from sqlalchemy.orm import relationship # para usar JOIN
from datetime import datetime
from typing import Union
from model import Base  # , Comentario

class Estabelecimento(Base):
    __tablename__ = "estabelecimentos"

    id = Column("pk_estabelecimento", Integer, primary_key=True)
    nome = Column(String(100))
    descricao = Column(String(200))
    endereco = Column(String(200), unique=True)
    data_de_cadastro = Column(DateTime, default=datetime.now())
    
    def __init__(self,id:int,nome:str,descricao:str,endereco:str):
        """
        Cadastra um novo estabelecimento no banco de dados
        id: id do estabelecimento
        nome: nome do estabelecimento
        descricao: descricao do estabelecimento
        endereco: endereco do estabelecimento
        data_de_cadastro:  data de cadastro do estabelecimento
        """
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.endereco = endereco
        self.data_de_cadastro = datetime.now()