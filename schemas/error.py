from pydantic import BaseModel

class ErrorSchema(BaseModel):
    """ Define como uma mensagem de erro será representada
    """
    mesage: str
    
class ErrorUploadSchema(BaseModel):
    """ Define como uma mensagem de erro no upload será representada
    """
    status: str
    mesage: str
    arquivo: str