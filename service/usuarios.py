from sqlalchemy import Column, String, Integer, DateTime, Date 

from datetime import datetime
from typing import Union
from model import Base 

from werkzeug.security import generate_password_hash, check_password_hash

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