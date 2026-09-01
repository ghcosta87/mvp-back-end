# ==========================================
# 1. BIBLIOTECAS NATIVAS DO PYTHON
# ==========================================
import os
import io
import logging
from sqlite3 import IntegrityError
import warnings
from datetime import date

# from urllib.parse import unquote

# ==========================================
# 2. BIBLIOTECAS DE TERCEIROS (pip install)
# ==========================================
# Variáveis de ambiente
from dotenv import load_dotenv, find_dotenv

# Flask, CORS e Swagger (Servidor Web e API)
from flask import redirect  # , request
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info, Tag

# Inteligência Artificial (Google Gemini)
from google import genai
from google.genai.types import GenerateContentConfig

# Imagens e Conversões
from PIL import Image
from pillow_heif import register_heif_opener

# from sqlalchemy import JSON

# ==========================================
# 3. MÓDULOS DO SEU PROJETO (Arquivos Locais)
# ==========================================
# Constantes
import model.constants as const

# Banco de Dados
from model import Session
from model.produto import Produto
from model.usuarios import Usuario

# Schemas (Validação de Dados)
from schemas.usuarios import UsuarioSchema, UsuarioBuscaSchema, apresenta_usuario
from schemas.produto import CupomExtraidoSchema, ProdutoSchema
from schemas.upload import UploadSchema
from schemas.error import ErrorSchema, ErrorUploadSchema

# ==========================================
# DEFINIÇÃO DAS HOME TAGS
# ==========================================
tag_user = Tag(name="Usuários", description="Funções de controle de usuários")
tag_image = Tag(
    name="Imagens", description="Funções de upload e processamento de imagens"
)
tag_produtos = Tag(name="Produtos", description="Funções de listagem de produtos")

# ==========================================
# CONFIGURAÇÕES GLOBAIS
# ==========================================

load_dotenv(find_dotenv())
chave_api = os.getenv("API_KEY")
client = genai.Client(api_key=chave_api)

logging.getLogger("google.genai").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*automatic function calling.*")

register_heif_opener()  # Liga o suporte a HEIC dentro do Pillow

info = Info(title="Minha API", version="0.0.1")
app = OpenAPI(__name__, info=info)
CORS(app)


@app.post(
    "/adicionar_usuario",
    tags=[tag_user],
    responses={"200": UsuarioSchema, "409": ErrorSchema, "400": ErrorSchema},
)
def add_usuario(body: UsuarioSchema):
    """Adiciona um novo Usuário à base de dados."""
    data_convertida = date.fromisoformat(body.nascimento)

    usuario = Usuario(
        nome_completo=body.nome_completo,
        cpf=body.cpf,
        email=body.email,
        nascimento=data_convertida,
        telefone=body.telefone,
        senha=body.senha,
    )

    try:
        session = Session()
        session.add(usuario)
        session.commit()
        session.close()
        return apresenta_usuario(usuario), 200
    except IntegrityError:
        return {"mesage": "CPF, E-mail ou Telefone já cadastrados."}, 409
    except Exception as e:
        return {"mesage": str(e)}, 400


@app.delete(
    "/deletar_usuario",
    tags=[tag_user],
    responses={
        "200": UsuarioSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
        "401": ErrorSchema,
    },
)
def deletar_usuario(body: UsuarioBuscaSchema):
    """Deleta um Usuário da base de dados."""
    try:
        success = False
        session = Session()
        usuario_encontrado = (
            session.query(Usuario).filter(Usuario.email == body.email).first()
        )

        if not usuario_encontrado:
            return {"error": const.ERROR_SQL_USER_NOT_FOUND}, 404

        if usuario_encontrado.verificar_senha(body.senha_digitada):
            session.delete(usuario_encontrado)
            session.commit()
            session.close()
            success = True

        if success:
            return {"message": const.SUCCESS_SQL_USER_DEL}, 200
        else:
            return {"message": const.ERROR_SQL_USER_WRONG_PASSWORD}, 401

    except Exception as e:
        session.rollback()
        return {"error": f"{const.ERROR_SQL_USER_DEL} {str(e)}"}, 400


@app.post(
    "/login",
    tags=[tag_user],
    responses={
        "200": UsuarioSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
        "401": ErrorSchema,
    },
)
def logar(body: UsuarioBuscaSchema):
    """Verifica se o usuário existe e se a senha está correta e retorna uma mensagem de sucesso ou erro."""
    try:
        session = Session()
        usuario_encontrado = (
            session.query(Usuario).filter(Usuario.email == body.email).first()
        )
        if not usuario_encontrado:
            return {"error": const.ERROR_SQL_USER_NOT_FOUND}, 404

        if usuario_encontrado.verificar_senha(body.senha_digitada):
            return {
                "message": "Login realizado com sucesso",
                "email": usuario_encontrado.email,
            }, 200
        else:
            return {"error": const.ERROR_SQL_USER_WRONG_PASSWORD}, 401

    except Exception as e:
        session.rollback()
        return {"error": f"{const.ERROR_SQL_USER_DEL} {str(e)}"}, 400


@app.post(
    "/upload",
    tags=[tag_image],
    responses={
        "200": UploadSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
        "500": ErrorUploadSchema,
    },
)
def upload_imagem(form: UploadSchema):
    """
    Recebe a imagem, valida, filtra e adiciona os produtos ao banco de dados.
    """
    file = form.imagem
    file.seek(0)
    image_bytes = file.read()

    if not image_bytes:
        return {"error": const.ERROR_EMPTY_IMAGE}, 400
    if file.filename == "":
        return {"error": const.ERROR_EMPTY_FILE}, 400

    try:
        # 1. PROCESSAMENTO DA IA
        imagem_original = Image.open(io.BytesIO(image_bytes))
        imagem_tratada = imagem_original.convert("RGB")

        response = client.models.generate_content(
            model=const.GEMINI_MODEL,
            contents=[imagem_tratada, const.PROMPT],
            config=GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CupomExtraidoSchema,
                temperature=0.1,
            ),
        )
        dados = response.parsed.model_dump()

    except Exception as e:
        return {
            "status": "erro",
            "message": f"{const.ERROR_GEMINI_IMAGE_PROCESS} {str(e)}",
            "arquivo_recebido": file.filename,
        }, 500

    # 2. SALVAMENTO NO BANCO DE DADOS
    session = Session()
    produtos_salvos = []

    try:
        for item in dados["produtos"]:
            produto = Produto(
                id=None,
                nome=item["nome"],
                marca=item.get(
                    "marca", "Sem marca"
                ),  # Fallback seguro caso a IA não encontre
                preco=item["preco"],
            )
            session.add(produto)
            produtos_salvos.append(produto.nome)

        session.commit()
        return {
            "status": "sucesso",
            "message": f"{len(produtos_salvos)} {const.SUCCESS_SQL_PRODUCT_ADD}",
            "produtos_extraidos": dados["produtos"],
        }, 200
    except Exception as e:
        session.rollback()
        print(f"{const.ERROR_SQL_PRODUCT_ADD} {str(e)}")
        return {
            "status": "erro",
            "message": f"{const.ERROR_SQL_PRODUCT_ADD} {str(e)}",
            "arquivo": file.filename,
        }, 500
    finally:
        session.close()


@app.get(
    "/produtos",
    tags=[tag_produtos],
    responses={
        "200": ProdutoSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
        "401": ErrorSchema,
    },
)
def listar_produtos():
    """
    Retorna todos os produtos cadastrados no banco de dados
    """
    lista_produtos = []

    try:
        session = Session()
        produtos_db = session.query(Produto).all()

        for produto in produtos_db:
            lista_produtos.append(
                {"id": produto.id, "nome": produto.nome, "preco": float(produto.preco)}
            )
        session.close()
        return {"produtos": lista_produtos}, 200

    except Exception as e:
        return {"error": f"O Python reclamou disso: {str(e)}"}, 500
