from pydantic import BaseModel,Field, field_validator
from typing import Optional, List
from model.usuarios import Usuario

# from schemas import ComentarioSchema

class UsuarioSchema(BaseModel):
    """ Define como um novo usuário a ser inserido deve ser representado
    """
    nome_completo: str = "Gabriel Silva"
    cpf: str = "123.456.789-00"
    email: str = "gabriel.silva@example.com"
    nascimento: Optional[str] = "1990-01-01"
    telefone: int = 1234567890
    senha: str = "123"
    
    @field_validator('senha', mode='before')
    @classmethod
    def garantir_string(cls, v):
        # Converte qualquer dado (inclusive números puros como 6666) para string antes da validação
        return str(v) if v is not None else ""
     
class UsuarioBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no nome do usuário.
    """
    email: str = "gabriel.silva@example.com"
    senha_digitada: str = "senha123"
    
    @field_validator('senha_digitada', mode='before')
    @classmethod
    def garantir_string(cls, v):
        # Converte qualquer dado (inclusive números puros como 6666) para string antes da validação
        return str(v) if v is not None else ""
    
class ListagemUsuariosSchema(BaseModel):
    """ Define como uma listagem de usuários será retornada.
    """
    usuarios: List[UsuarioSchema]
    
def apresenta_usuario(usuario: Usuario):
    """ Retorna uma representação do usuário seguindo o schema definido em
        UsuarioViewSchema.
    """
    return {
        "nome_completo": usuario.nome_completo,
        "cpf": usuario.cpf,
        "email": usuario.email,
        "nascimento": usuario.nascimento.isoformat(), #if usuario.nascimento else None,
        "telefone": usuario.telefone,
        "senha": usuario.senha,
        "data_de_cadastro": usuario.data_de_cadastro.isoformat() #if usuario.data_de_cadastro else None
    }
    
    