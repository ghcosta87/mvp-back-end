from pydantic import BaseModel
from flask_openapi3 import FileStorage

class UploadSchema(BaseModel):
    """ Schema para validar o upload de uma imagem """
    # Essa configuração avisa ao Pydantic que FileStorage é um tipo válido
    # model_config = ConfigDict(arbitrary_types_allowed=True) 
    
    # O nome 'imagem' deve ser o mesmo usado no formData do front-end
    imagem: FileStorage