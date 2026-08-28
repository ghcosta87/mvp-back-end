import io

import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig

# from tkinter import Image
from PIL import Image
import types
# from xmlrpc import client

from flask_openapi3 import OpenAPI, Info, Tag
from flask import jsonify, redirect, request
from urllib.parse import unquote

# from sqlalchemy.exc import IntegrityError

from model import Session, Produto  # , Comentario
from model.usuarios import *

# from logger import logger
# from mvp.back.schemas import *
from flask_cors import CORS
from schemas import *

from datetime import date

# from mvp.back.schemas.produto import ProdutoSchema, apresenta_produto

from PIL import Image
from pillow_heif import register_heif_opener
import io

# Liga o suporte a HEIC dentro do Pillow
register_heif_opener()

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
        senha=form.senha,
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


@app.delete("/deletar_usuario")  # , tags=[usuario_tag])
def deletar_usuario(query: UsuarioBuscaSchema):
    session = Session()
    try:
        # 1. Busca o usuário no banco de dados (ex: pelo email ou CPF)
        usuario_encontrado = (
            session.query(Usuario).filter(Usuario.email == query.email).first()
        )

        # 2. Verifica se o usuário realmente existe
        if not usuario_encontrado:
            return {"error": "Usuário não encontrado na base de dados."}, 404

        if usuario_encontrado.verificar_senha(query.senha_digitada):
            session.delete(usuario_encontrado)
            session.commit()
            return {"message": "Usuário deletado com sucesso!"}, 200

    except Exception as e:
        # Se der erro, desfaz qualquer alteração pela metade (rollback)
        session.rollback()
        return {"error": f"Não foi possível deletar o usuário: {str(e)}"}, 400

    finally:
        # Sempre fecha a conexão para não sobrecarregar o servidor
        session.close()


####################################
#####################
###########
# AQUI TEM QUE SABER COMO VOU ENVIAR AS IMAGENS PARA O POST

# Importe o schema que você criou (ajuste de acordo com o arquivo onde você o salvou)
from schemas import UploadSchema 

@app.post('/upload')#, tags=[produto_tag])
def upload_imagem(form: UploadSchema): # <-- Passamos o schema aqui!
    """
    Recebe a imagem, valida e retorna sucesso.
    """
    file = form.imagem
    
    # 1. Rebobina e lê os bytes
    file.seek(0)
    image_bytes = file.read()
    
    load_dotenv(find_dotenv())
    chave_api = os.getenv("API_KEY")

    # 2. Cria o cliente OFICIAL do Gemini (esta é a variável que o seu código precisa!)
    client = genai.Client(api_key=chave_api)
    
    if not image_bytes:
            return {"error": "Os bytes da imagem estão vazios."}, 400
    
    # Verifica se o arquivo não está corrompido ou vazio
    if file.filename == '':
        return {"error": "O arquivo enviado está vazio."}, 400
    
    print("Testando conexão com o Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents="Responda apenas 'Olá' se você estiver me ouvindo."
        )
        print(f"Resposta do Gemini: {response.text}")
        # return {"mensagem": response.text}
    except Exception as e:
        return {"erro": str(e)}

    # ==========================================
    # CÓDIGO DA IA ENTRARÁ AQUI
    # ==========================================
    try:
        # 2. Abre a imagem (agora o código entende HEIC!)
        imagem_original = Image.open(io.BytesIO(image_bytes))
        
        # 3. Converte para o padrão visual RGB (remove camadas ocultas do HEIC)
        imagem_tratada = imagem_original.convert("RGB")
        
        #  Converte os bytes recebidos diretamente para uma imagem PIL
        # image_bytes = file.read()
        # imagem = Image.open(io.BytesIO(image_bytes))
        
        #prompt = "Extraia o estabelecimento, a data (YYYY-MM-DD) e a lista de produtos com preços unitários finais."
        prompt = "Extraia a data (YYYY-MM-DD) e a lista de produtos com preços unitários finais e suas respectivas marcas tentando dar o nome completo aos produtos."

        # Chamada para o Gemini
        # response = client.models.generate_content(
        response = client.chats.create(
            # gemini-3.6-flash
            # model="gemini-2.5-flash",
            model="gemini-3.6-flash",
            contents=[imagem_tratada, prompt],
            # config=types.GenerateContentConfig(
            config=GenerateContentConfig(
                response_mime_type="application/json",
                # response_schema=Produto,  # ,Estabelecimento
                response_schema=CupomExtraidoSchema,                                
                temperature=0.1,
            ),
        )
        response = client.chats.send_message([imagem_tratada, prompt])
        # Retorna o JSON processado diretamente para o frontend
        dados = response.parsed.model_dump()
        return dados,200
        
        # TODO: Aqui você executa os INSERTS no seu banco SQL usando o 'dados'
        # return jsonify(dados)
        
        ########################################
        # data_convertida = date.fromisoformat(
        #         form.nascimento
        #     )  # if form.nascimento else None
        
        #     usuario = Usuario(
        #         nome_completo=form.nome_completo,
        #         cpf=form.cpf,
        #         email=form.email,
        #         nascimento=data_convertida,
        #         telefone=form.telefone,
        #         senha=form.senha,
        #     )
        #     # logger.debug(f"Adicionando produto de nome: '{produto.nome}'")
        ########################################        
        # try:
        #     session = Session()
        #     session.add(produto)
        #     session.commit()
        #     return apresenta_produto(produto), 200
        # except Exception as e:
        #     return {"error": str(e)}, 400
        ########################################
        
        
        
    except Exception as e:
        return {
            "status": "erro", 
            "message": f"Erro ao processar a imagem: {str(e)}",
            "arquivo_recebido": file.filename
        }, 500
    
    # Retorna o JSON de sucesso
    return {
        "status": "sucesso", 
        "message": "A imagem chegou perfeitamente no servidor Flask!",
        
        "arquivo_recebido": file.filename
    }, 200
    
# @app.post(
#     "/upload"
# )  # , tags=[produto_tag],responses={"200": ProdutoViewSchema, "409": ErrorSchema, "400": ErrorSchema},)
# def processar_imagem(form: ProdutoSchema):
#     if "imagem" not in request.files:
#         return jsonify({"erro": "Nenhuma imagem enviada"}), 400

#     file = request.files["imagem"]

#     if file.filename == "":
#         return {"error": "O arquivo enviado está vazio."}, 400

#     # Converte os bytes recebidos diretamente para uma imagem PIL
#     image_bytes = file.read()
#     imagem = Image.open(io.BytesIO(image_bytes))
#     prompt = "Extraia o estabelecimento, a data (YYYY-MM-DD) e a lista de produtos com preços unitários finais."
#     # Chamada para o Gemini
#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=[imagem, prompt],
#         config=types.GenerateContentConfig(
#             response_mime_type="application/json",
#             response_schema=Produto,  # ,Estabelecimento
#             temperature=0.1,
#         ),
#     )
#     # Retorna o JSON processado diretamente para o frontend
#     dados = response.parsed.model_dump()
#     # TODO: Aqui você executa os INSERTS no seu banco SQL usando o 'dados'
#     # return jsonify(dados)

#     return {
#         "status": "sucesso",
#         "message": "A imagem chegou perfeitamente no servidor Flask!",
#         "arquivo_recebido": file.filename,
#     }, 200

#     # if __name__ == '__main__':
#     #         # HTTPS é necessário em produção para liberar acesso à câmera
#     #     app.run(debug=True)
