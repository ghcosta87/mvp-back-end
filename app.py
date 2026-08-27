import io
# from tkinter import Image
from PIL import Image
import types
from xmlrpc import client

from flask_openapi3 import OpenAPI, Info, Tag
from flask import jsonify, redirect, request
from urllib.parse import unquote

# from sqlalchemy.exc import IntegrityError

from model import Session, Usuario, Produto  # , Comentario

# from logger import logger
# from mvp.back.schemas import *
from flask_cors import CORS
from schemas import *

from datetime import date

# from mvp.back.schemas.produto import ProdutoSchema, apresenta_produto

info = Info(title="Minha API", version="0.0.1")
app = OpenAPI(__name__, info=info)
CORS(app)


@app.get("/")  # , tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")


@app.post(
    "/usuario"
)  # , tags=[produto_tag],responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema},)
def add_usuario(form: UsuarioSchema):
    """Adiciona um novo Usuário à base de dados

    Retorna uma representação dos usuários e comentários associados.
    """
    data_convertida = date.fromisoformat(
        form.nascimento
    )  # if form.nascimento else None

    usuario = Usuario(
        nome_completo=form.nome_completo,
        cpf=form.cpf,
        email=form.email,
        nascimento=data_convertida,
        telefone=form.telefone,
    )
    # logger.debug(f"Adicionando produto de nome: '{produto.nome}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando produto
        session.add(usuario)
        # efetivando o camando de adição de novo item na tabela
        session.commit()
        # logger.debug(f"Adicionado produto de nome: '{produto.nome}'")
        return apresenta_usuario(usuario), 200
    # except IntegrityError:
    #     return {"error": "CPF, E-mail ou Telefone já cadastrados."}, 409
    except Exception as e:
        return {"error": str(e)}, 400

    # except IntegrityError as e:
    #     # como a duplicidade do nome é a provável razão do IntegrityError
    #     error_msg = "Produto de mesmo nome já salvo na base :/"
    #     logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
    #     return {"mesage": error_msg}, 409

    # except Exception as e:
    #     # caso um erro fora do previsto
    #     error_msg = "Não foi possível salvar novo item :/"
    #     logger.warning(f"Erro ao adicionar produto '{produto.nome}', {error_msg}")
    #     return {"mesage": error_msg}, 400


####################################
#####################
###########
# AQUI TEM QUE SABER COMO VOU ENVIAR AS IMAGENS PARA O POST

@app.post(
    "/upload"
)  # , tags=[produto_tag],responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema},)

def processar_imagem(form: ProdutoSchema):
    if 'imagem' not in request.files:
        return jsonify({"erro": "Nenhuma imagem enviada"}), 400
    
    file = request.files['imagem']
    # Converte os bytes recebidos diretamente para uma imagem PIL
    image_bytes = file.read()
    imagem = Image.open(io.BytesIO(image_bytes))
    prompt = "Extraia o estabelecimento, a data (YYYY-MM-DD) e a lista de produtos com preços unitários finais."
    # Chamada para o Gemini
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[imagem, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Produto, #,Estabelecimento
            temperature=0.1
        ),
    )
     # Retorna o JSON processado diretamente para o frontend
    dados = response.parsed.model_dump()
    # TODO: Aqui você executa os INSERTS no seu banco SQL usando o 'dados'
    return jsonify(dados)

    if __name__ == '__main__':
            # HTTPS é necessário em produção para liberar acesso à câmera
        app.run(debug=True)