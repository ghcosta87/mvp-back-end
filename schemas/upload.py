from pydantic import BaseModel

# ❌ APAGUE a linha antiga do Werkzeug e o ConfigDict:
# from pydantic import ConfigDict
# from werkzeug.datastructures import FileStorage

# ✅ ADICIONE a importação oficial do flask_openapi3:
from flask_openapi3 import FileStorage

class UploadSchema(BaseModel):
    """ Schema para validar o upload de uma imagem """
    # Essa configuração avisa ao Pydantic que FileStorage é um tipo válido
    # model_config = ConfigDict(arbitrary_types_allowed=True) 
    
    # O nome 'imagem' deve ser o mesmo usado no formData do front-end
    imagem: FileStorage