from sqlalchemy import Column, String, Integer, DateTime, Date  # ,Float

# from sqlalchemy.orm import relationship # para usar JOIN
from datetime import datetime
from typing import Union
from model import Base  # , Comentario

from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("pk_usuario", Integer, primary_key=True)
    nome_completo = Column(String)
    cpf = Column(String(14), unique=True)
    email = Column(String, unique=True)
    nascimento = Column(Date)
    telefone = Column(String(11), unique=True)
    senha = Column(String(255), nullable=False)
    data_de_cadastro = Column(DateTime, default=datetime.now())

    def __init__(
        self,
        nome_completo: str,
        cpf: str,
        email: str,
        nascimento: Union[Date],
        telefone: int,
        senha: str,
    ):
        """
        Cadastra um novo usuário no banco de dados
        nome_completo: Nome completo do usuário
        cpf: cadastro de pessoa física do usuário
        email: email do usuário
        nascimento: data de nascimento do usuário
        telefone: telefone do usuário
        senha: senha do usuário
        data_de_cadastro:  data de cadastro do usuário
        """
        self.nome_completo = nome_completo
        self.cpf = cpf
        self.email = email
        self.nascimento = nascimento
        self.telefone = telefone
        self.senha = generate_password_hash(senha, method='pbkdf2:sha256')
        self.data_de_cadastro = datetime.now()

    def verificar_senha(self, senha_digitada: str) -> bool:
        """
        Recebe a senha que o usuário digitou no login e compara com o Hash salvo.
        Retorna True se estiver correta, False se estiver errada.
        """
        return check_password_hash(self.senha, senha_digitada)
    
    # def apagar_usuario(self,senha_digitada: str):
    #     """
    #     Apaga o usuário do banco de dados.
    #     """
    #     from model import Session  # Importa a sessão do SQLAlchemy

    #     session = Session()
    #     session.delete(self)
    #     session.commit()