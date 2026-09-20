from pydantic import BaseModel

class ErrorSchema(BaseModel):
    """ Define como uma mensagem de erro será representada
    """
    message: str
    error: str
    
class ErrorUploadSchema(BaseModel):
    """ Define como uma mensagem de erro no upload será representada
    """
    status: str
    message: str
    file: str