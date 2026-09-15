# ==========================================
# 1. BIBLIOTECAS NATIVAS DO PYTHON
# ==========================================
import os
import io
import logging
from logging.handlers import RotatingFileHandler
from sqlite3 import IntegrityError
from sqlalchemy import func

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

# Imagens e Conversões
from PIL import Image
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
tag_home = Tag(
    name="Home", description="Função de redirecionamento para a documentação da API"
)

# ==========================================
# CONFIGURAÇÕES GLOBAIS
# ==========================================

load_dotenv(find_dotenv())
chave_api = os.getenv("API_KEY")

# warnings.filterwarnings("ignore", message=".*automatic function calling.*")
from logger import logger

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "logs/debug.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
    ],
)
logging.getLogger("google.genai").setLevel(logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.DEBUG)
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

register_heif_opener()  # Liga o suporte a HEIC dentro do Pillow

info = Info(title="Minha API", version="0.0.1")
app = OpenAPI(__name__, info=info)
CORS(app)

logger.info(f"Aplicatição iniciada")


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
        return {
            "message": "CPF, E-mail ou Telefone já cadastrados." # <?> adicionar constant de texto
        }, HTTPStatus.CONFLICT
    except Exception as e:
        return {"message": str(e)}, HTTPStatus.BAD_REQUEST
    finally:
        session.close()


@app.post( # <?> atualizar as respostas dos esquemas
    "/deletar_usuario",
    tags=[tag_user],
    responses={
        HTTPStatus.OK: UsuarioSchema,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
        HTTPStatus.UNAUTHORIZED: ErrorSchema,
        HTTPStatus.CONFLICT: ErrorSchema, # ?
        HTTPStatus.UNPROCESSABLE_ENTITY: ErrorSchema # ?
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
            return {"error": const.ERROR_SQL_USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        if usuario_encontrado.verificar_senha(form.senha_digitada):
            session.delete(usuario_encontrado)
            session.commit()
            session.close()
            success = True

        if success:
            return {"message": const.SUCCESS_SQL_USER_DEL}, HTTPStatus.OK
        else:
            return {"message": const.ERROR_SQL_USER_WRONG_PASSWORD}, HTTPStatus.UNAUTHORIZED

    except Exception as e:
        session.rollback()
        return {"error": f"{const.ERROR_SQL_USER_DEL} {str(e)}"}, HTTPStatus.BAD_REQUEST


@app.post(
    "/login",
    tags=[tag_user],
    responses={
        HTTPStatus.OK: UsuarioSchema,
        HTTPStatus.UNAUTHORIZED: ErrorSchema,
        HTTPStatus.NOT_FOUND: ErrorSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
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
            return {"message": const.ERROR_SQL_USER_NOT_FOUND}, HTTPStatus.NOT_FOUND

        if usuario_encontrado.verificar_senha(body.senha_digitada):
            return {
                "message": "Login realizado com sucesso", # <?> atualizar ocm constantes de string
                "email": usuario_encontrado.email,
            }, 200
        else:
            return {
                "message": const.ERROR_SQL_USER_WRONG_PASSWORD
            }, HTTPStatus.UNAUTHORIZED

    except Exception as e:
        session.rollback()
        return {
            "message": f"{const.ERROR_SQL_USER_DEL} {str(e)}"
        }, HTTPStatus.INTERNAL_SERVER_ERROR


@app.post(
    "/upload",
    tags=[tag_image],
    responses={
        HTTPStatus.OK: UploadSchema,
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
                # http_options=HttpOptions(
                #     timeout=30000clo
                # ),  # timeout em milissegundos # precisa de mais tests
            ),
        )
        dados = response.parsed.model_dump()

    except Exception as e:
        return {
            "status": "erro",
            "message": f"{const.ERROR_GEMINI_IMAGE_PROCESS} {str(e)}",
            "file": file.filename,
        }, HTTPStatus.GATEWAY_TIMEOUT
    finally:
        print(f"${datetime.now()} função upload_imagem finalizada.")

    # 2. SALVAMENTO NO BANCO DE DADOS
    session = Session()
    produtos_salvos = []

    try:
        if "loja" in dados:
            loja_dados = dados["loja"]
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
                ),  # Fallback seguro caso a IA não encontre
                data_da_compra=item.get("data", datetime.now()),
                preco=item["preco"],
            )
            session.add(produto)
            produtos_salvos.append(produto.nome)

        session.commit()
        return {
            "status": "sucesso",
            "message": f"{len(produtos_salvos)} {const.SUCCESS_SQL_PRODUCT_ADD}",
            "produtos_extraidos": dados["produtos"],
        }, HTTPStatus.OK
        
    except Exception as e:
        session.rollback()
        print(f"{const.ERROR_SQL_PRODUCT_ADD} {str(e)}")
        print(f"lista de produtos extraídos: {dados['produtos']}")
        return {
            "status": "erro",
            "message": f"{const.ERROR_SQL_PRODUCT_ADD} {str(e)}",
            "arquivo": file.filename,
        }, HTTPStatus.INTERNAL_SERVER_ERROR
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
def listar_produtos(): # <?> rever completo
    """
    Retorna todos os produtos cadastrados no banco de dados
    """
    logger.info(f"Requisição recebida em /produtos")

    lista_produtos = []

    try:
        session = Session()
        logger.info(f"Iniciada secção do banco de dados")

        produtos_db = session.query(Produto).all()

        for produto in produtos_db:
            lista_produtos.append(
                {
                    "id": produto.id,
                    "nome": produto.nome,
                    "data_da_compra": produto.data_da_compra,
                    "preco": float(produto.preco),
                }
            )

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

        # return {"estatisticas": dados_formatados}, 200

        logger.info(f"Fechando banco de dados")
        session.close()
        logger.info(f"Termino da função listar_produtos sem erros")

        return {
            "produtos": lista_produtos,
            "estatisticas": resultado_formatados,
            "historico": historico_agrupado,
        }, 200

    except Exception as e:

        logger.error(f"O Python reclamou disso: {str(e)}, retornando código 500")
        return {"error": f"O Python reclamou disso: {str(e)}"}, 500


@app.post(
    "/join_product",
    tags=[tag_produtos],# <?> remover, marcar como teste ou terminar de implementar
    responses={
        HTTPStatus.OK: UsuarioSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
        "401": ErrorSchema,
    },
)
def juntar_produtos(): 

    return 0


if __name__ == "__main__":
    app.run(debug=True, threaded=True)