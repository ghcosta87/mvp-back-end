# ==========================================
# 1. BIBLIOTECAS NATIVAS DO PYTHON
# ==========================================
import os
import io
import logging
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

# import warnings
from datetime import date, datetime

# ==========================================
# 2. BIBLIOTECAS DE TERCEIROS (pip install)
# ==========================================
# Variáveis de ambiente
from dotenv import load_dotenv, find_dotenv

# Flask, CORS e Swagger (Servidor Web e API)
from flask import redirect
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info, Tag

# Inteligência Artificial (Google Gemini)
from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions
from httpx import TimeoutException

# Imagens e Conversões
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

from http import HTTPStatus

# ==========================================
# 3. MÓDULOS DO SEU PROJETO (Arquivos Locais)
# ==========================================
# Constantes
import model.constants as const

# Banco de Dados
from model import Session
from model.produto import Produto
from model.usuarios import Usuario
from model.estabelecimento import Estabelecimento

# Schemas (Validação de Dados)
from schemas.usuarios import UsuarioSchema, UsuarioBuscaSchema, apresenta_usuario
from schemas.produto import CupomExtraidoSchema, ProdutoSchema, ConsultaSchema
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
tag_home = Tag(
    name="Home", description="Função de redirecionamento para a documentação da API"
)

# ==========================================
# CONFIGURAÇÕES GLOBAIS
# ==========================================

load_dotenv(find_dotenv())
chave_api = os.getenv("API_KEY")

register_heif_opener()  # Liga o suporte a HEIC dentro do Pillow

info = Info(title="Minha API", version="0.0.1")
app = OpenAPI(__name__, info=info)
CORS(app)

@app.get("/", tags=[tag_home])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")

@app.post(
    "/adicionar_usuario",
    tags=[tag_user],
    responses={
        HTTPStatus.OK: UsuarioSchema,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
        HTTPStatus.UNAUTHORIZED: ErrorSchema,
        HTTPStatus.CONFLICT: ErrorSchema,
        HTTPStatus.UNPROCESSABLE_ENTITY: ErrorSchema,
    },
)
def add_usuario(form: UsuarioSchema):
    """Adiciona um novo Usuário à base de dados."""
    data_convertida = date.fromisoformat(form.nascimento)

    usuario = Usuario(
        nome_completo=form.nome_completo,
        cpf=form.cpf,
        email=form.email,
        nascimento=data_convertida,
        telefone=form.telefone,
        senha=form.senha,
    )

    try:
        session = Session()
        session.add(usuario)
        session.commit()
        return apresenta_usuario(usuario), HTTPStatus.OK
    
    except IntegrityError:
        session.rollback()
        return {
            "message": const.ERROR_SQL_USER_ALREADY_IN_DATABASE
        }, HTTPStatus.CONFLICT
        
    except Exception as e:
        session.rollback()
        return {"message": const.ERROR_SQL_UNKNOWN}, HTTPStatus.BAD_REQUEST
    
    finally:
        session.close()

@app.post( 
    "/deletar_usuario",
    tags=[tag_user],
    responses={
        HTTPStatus.OK: UsuarioSchema,
        HTTPStatus.BAD_REQUEST: ErrorSchema, # somente se o tiver problemas na base de dados
        HTTPStatus.UNAUTHORIZED: ErrorSchema, # erro de senha
        HTTPStatus.NOT_FOUND: ErrorSchema, # somente se o usuario forçar o login
    },
)
def deletar_usuario(form: UsuarioBuscaSchema):
    """Deleta um Usuário da base de dados."""
    print(f"email do usuario para deletar: ${form.email}")
    try:
        success = False
        session = Session()
        usuario_encontrado = (
            session.query(Usuario).filter(Usuario.email == form.email).first()
        )

        if not usuario_encontrado:
            return {"message": const.ERROR_SQL_USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        if usuario_encontrado.verificar_senha(form.senha_digitada):
            session.delete(usuario_encontrado)
            session.commit()
            success = True

        if success:
            return {"message": const.SUCCESS_SQL_USER_DEL}, HTTPStatus.OK
        else:
            return {"message": const.ERROR_SQL_USER_WRONG_PASSWORD}, HTTPStatus.UNAUTHORIZED

    except Exception as e:
        session.rollback()
        return {"message": f"{const.ERROR_SQL_USER_DEL} {str(e)}"}, HTTPStatus.BAD_REQUEST

    finally:
        session.close()

@app.post(
    "/login",
    tags=[tag_user],
    responses={
        HTTPStatus.OK: UsuarioSchema,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
        HTTPStatus.UNAUTHORIZED: ErrorSchema,
        HTTPStatus.NOT_FOUND: ErrorSchema        
    },
)
def logar(form: UsuarioBuscaSchema):
    """Verifica se o usuário existe e se a senha está correta e retorna uma mensagem de sucesso ou erro."""
    try:
        session = Session()
        usuario_encontrado = (
            session.query(Usuario).filter(Usuario.email == form.email).first()
        )

        if not usuario_encontrado:
            logging.info(form.email)
            return {"message": const.ERROR_SQL_USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        if usuario_encontrado.verificar_senha(form.senha_digitada):
            return {
                "message": const.SUCCESS_LOGIN_AUTHORIZED,
                "email": usuario_encontrado.email,
            }, HTTPStatus.OK
        else:
            return {
                "message": const.ERROR_SQL_USER_WRONG_PASSWORD
            }, HTTPStatus.UNAUTHORIZED

    except Exception as e:
        session.rollback()
        return {
            "message": f"{const.ERROR_SQL_USER_DEL} {str(e)}"
        }, HTTPStatus.BAD_REQUEST
    finally:
        session.close()

@app.post(
    "/upload",
    tags=[tag_image],
    responses={
        HTTPStatus.OK: UploadSchema,
        HTTPStatus.LENGTH_REQUIRED:ErrorUploadSchema,
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE:ErrorSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR:ErrorUploadSchema,
        HTTPStatus.GATEWAY_TIMEOUT: ErrorUploadSchema
    },
)
def upload_imagem(form: UploadSchema): # <?> rever e limpar comentarios
    """
    Recebe a imagem, valida, filtra e adiciona os produtos ao banco de dados.
    """

    file = form.imagem
    file.seek(0)
    image_bytes = file.read()

    if not image_bytes or file.filename == "":  #
        return {"message": const.ERROR_EMPTY_IMAGE}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    try:
        # 1. PROCESSAMENTO DA IA
        imagem_original = Image.open(io.BytesIO(image_bytes))
        imagem_tratada = imagem_original.convert("RGB")

        client = genai.Client(api_key=chave_api)

        response = client.models.generate_content(
            model=const.GEMINI_MODEL,
            contents=[imagem_tratada, const.PROMPT],
            config=GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CupomExtraidoSchema,
                temperature=0.1,
                http_options=HttpOptions(
                    timeout=const.GEMINI_MAX_WAITING_TIME
                ), 
            ),
        )
        dados = response.parsed.model_dump()

    except UnidentifiedImageError as err:
        logging.error(const.IMAGE_NOT_COMPATIBLE)
        return {
                    "status": "erro",
                    "message": const.ERROR_GEMINI_WRONG_FORMAT,
                    "arquivo": file.filename,
                }, HTTPStatus.UNSUPPORTED_MEDIA_TYPE       
        
    except TimeoutException as err:
        logging.error(const.GEMINI_NOT_RESPONDING)
        return {
                    "status": "erro",
                    "message": const.ERROR_GEMINI_TIMEOUT,
                    "arquivo": file.filename,
                }, HTTPStatus.GATEWAY_TIMEOUT       
        
    except Exception as e:
        logging.error("Erro desconhecido...")
        return {
            "status": "erro",
            "message": f"{const.ERROR_GEMINI_IMAGE_PROCESS} {str(e)}",
            "file": file.filename,
        }, HTTPStatus.INTERNAL_SERVER_ERROR

    # 2. SALVAMENTO NO BANCO DE DADOS
    session = Session()
    produtos_salvos = []

    try:
        if "loja" in dados:
            loja_dados = dados["loja"]
            lojaDuplicada=session.query(Estabelecimento).filter_by(endereco=loja_dados["endereco"]).first()
            if not lojaDuplicada:
                loja = Estabelecimento(
                    None,
                    loja_dados["nome"],
                    loja_dados["descricao"],
                    loja_dados["endereco"],
                )
                session.add(loja)

        for item in dados["produtos"]:
            produto = Produto(
                id=None,
                nome=item["nome"],
                marca=item.get(
                    "marca", "Sem marca"
                ), 
                data_da_compra=item.get("data", datetime.now()),
                preco=item["preco"],
            )
            session.add(produto)
            produtos_salvos.append(produto.nome)
        
        if not len(produtos_salvos):            
            logging.error(const.PRODUCT_NOT_FOUND)
            return{
                    "status": "erro",
                    "message": f"{len(produtos_salvos)} {const.ERROR_SQL_ADD_FROM_IMAGE}",
                    "arquivo": file.filename
                }, HTTPStatus.LENGTH_REQUIRED
                     
        session.commit()
        return {
            "status": "sucesso",
            "message": f"{len(produtos_salvos)} {const.SUCCESS_SQL_PRODUCT_ADD}",
            "produtos_extraidos": dados["produtos"],
        }, HTTPStatus.OK
                
    except Exception as e:
        session.rollback()
        return {
            "status": "erro",
            "message": f"{const.ERROR_SQL_UNKNOWN} {str(e)}",
            "arquivo": file.filename
        }, HTTPStatus.BAD_REQUEST
        
    finally:        
        session.close()

@app.get(
    "/produtos",
    tags=[tag_produtos],
    responses={
        HTTPStatus.OK: ConsultaSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema
    },
)
def listar_produtos():
    """
    Retorna todos os produtos cadastrados no banco de dados
    """
    try:
        session = Session()
        
        lista_produtos=[{
                         "id": produto.id,
                         "nome": produto.nome,
                         "data_da_compra": produto.data_da_compra,
                         "preco": float(produto.preco)
            }
            for produto in session.query(Produto).all()
        ]
        
        resultados = (
            session.query(
                Produto.nome,
                func.count(Produto.id).label("total_compras"),
                func.avg(Produto.preco).label("preco_medio"),
                func.min(Produto.preco).label("menor_preco"),
                func.max(Produto.preco).label("maior_preco"),
            )
            .group_by(Produto.nome)
            .all()
        )

        resultado_formatados = [
            {
                "nome": linha.nome,
                "total_compras": linha.total_compras,
                "preco_medio": round(linha.preco_medio, 2),
                "menor_preco": linha.menor_preco,
                "maior_preco": linha.maior_preco,
            }
            for linha in resultados
        ]

        historico = (
            session.query(Produto.nome, Produto.data_da_compra, Produto.preco)
            .order_by(Produto.nome, Produto.data_da_compra.asc())
            .all()
        )

        historico_agrupado = {}
        for linha in historico:
            historico_agrupado.setdefault(linha.nome, []).append(
                {
                    "data": (
                        linha.data_da_compra.isoformat()
                        if linha.data_da_compra
                        else None
                    ),
                    "valor": float(linha.preco),
                }
            )
        
        return {
            "produtos": lista_produtos,
            "estatisticas": resultado_formatados,
            "historico": historico_agrupado,
        }, HTTPStatus.OK

    except Exception as e:
        return {"error": f"{const.ERROR_SQL_UNKNOWN}: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    finally: session.close()
