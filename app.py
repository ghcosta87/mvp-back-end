# ==========================================
# 1. BIBLIOTECAS NATIVAS DO PYTHON
# ==========================================
import os
import io
import logging
import warnings
from datetime import date
from urllib.parse import unquote

# ==========================================
# 2. BIBLIOTECAS DE TERCEIROS (pip install)
# ==========================================
# Variáveis de ambiente
from dotenv import load_dotenv, find_dotenv

# Flask, CORS e Swagger (Servidor Web e API)
from flask import redirect, request
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info

# Inteligência Artificial (Google Gemini)
from google import genai
from google.genai.types import GenerateContentConfig

# Imagens e Conversões
from PIL import Image
from pillow_heif import register_heif_opener

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
from schemas.usuarios import UsuarioSchema, UsuarioBuscaSchema,apresenta_usuario
from schemas.produto import (
    CupomExtraidoSchema,
    ListagemProdutosSchema#,
)  # , ProdutoSchema, ListagemProdutosSchema, ItemExtraido
from schemas.upload import UploadSchema

# ==========================================
# CONFIGURAÇÕES GLOBAIS
# ==========================================

load_dotenv(find_dotenv())
chave_api = os.getenv("API_KEY")  # Verifique se no .env está API_KEY ou GEMINI_API_KEY
# Cria o cliente do Gemini permanentemente para o servidor usar
client = genai.Client(api_key=chave_api)

logging.getLogger("google.genai").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*automatic function calling.*")

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
def deletar_usuario(body: UsuarioBuscaSchema):
    session = Session()
    try:
        usuario_encontrado = (
            session.query(Usuario).filter(Usuario.email == body.email).first()
        )
        if not usuario_encontrado:
            return {"error": const.ERROR_SQL_USER_NOT_FOUND}, 404

        if usuario_encontrado.verificar_senha(body.senha_digitada):
            session.delete(usuario_encontrado)
            session.commit()
            return {"message": const.SUCCESS_SQL_USER_DEL}, 200
        else:
            return {"error": const.ERROR_SQL_USER_WRONG_PASSWORD}, 401

    except Exception as e:
        session.rollback()
        return {"error": f"{const.ERROR_SQL_USER_DEL} {str(e)}"}, 400

    finally:
        session.close()


@app.post("/login")  # , tags=[usuario_tag])
def logar(body: UsuarioBuscaSchema):
    session = Session()
    try:
        usuario_encontrado = (
            session.query(Usuario).filter(Usuario.email == body.email).first()
        )
        if not usuario_encontrado:
            return {"error": const.ERROR_SQL_USER_NOT_FOUND}, 404

        if usuario_encontrado.verificar_senha(body.senha_digitada):
         return {
                "message": "Login realizado com sucesso",
                "email": usuario_encontrado.email,
                # Se o seu model tiver 'nome' ou 'nome_completo', você pode retornar aqui:
                # "nome": usuario_encontrado.nome 
            }, 200
        else:
            return {"error": const.ERROR_SQL_USER_WRONG_PASSWORD}, 401

    except Exception as e:
        session.rollback()
        return {"error": f"{const.ERROR_SQL_USER_DEL} {str(e)}"}, 400

    finally:
        session.close()

@app.post("/upload")  # , tags=[produto_tag])
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
                nome=item["nome"],
                marca=item.get("marca", "Sem marca"), # Fallback seguro caso a IA não encontre
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
        return {
            "status": "erro",
            "message": f"{const.ERROR_SQL_PRODUCT_ADD} {str(e)}",
            "arquivo_recebido": file.filename,
        }, 500
    finally:
        session.close()

from flask import jsonify

# ... (suas outras rotas aqui)

# 1. O Schema vai no 'responses' indicando que é a SAÍDA da rota
@app.get('/produtos')#, tags=[produto_tag], responses={"200": ListagemProdutosSchema})
def listar_produtos(): # 2. A função agora não recebe parâmetros (GET limpo)
    session = Session()
    try:
        # Busca todos os produtos cadastrados no banco de dados
        produtos_db = session.query(Produto).all()
        
        # Cria uma lista vazia para armazenar os dados formatados
        lista_produtos = []
        
        # Transforma cada produto do banco em um dicionário
        for produto in produtos_db:
            lista_produtos.append({
                "id": produto.id,
                "nome": produto.nome,
                "preco": float(produto.preco) 
            })
            
        # 3. Devolve um DICIONÁRIO com a chave "produtos" (Flask-OpenAPI3 converte para JSON sozinho)
        return {"produtos": lista_produtos}, 200

    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        # return {"error": "Falha ao buscar produtos no banco de dados."}, 500
        return {"error": f"O Python reclamou disso: {str(e)}"}, 500
    
# @app.get('/produtos')#, methods=['GET'])
# def listar_produtos(form: ListagemProdutosSchema):
#     try:
#         # 1. Busca todos os produtos cadastrados no banco de dados
#         produtos_db = Produto.query.all()
        
#         # 2. Cria uma lista vazia para armazenar os dados formatados
#         lista_produtos = []
        
#         # 3. Transforma cada produto do banco em um dicionário (JSON)
#         for produto in produtos_db:
#             lista_produtos.append({
#                 "id": produto.id,
#                 "nome": produto.nome,
#                 # Garante que o preço vá como número (float) para o JS conseguir usar o .toFixed(2)
#                 "preco": float(produto.preco) 
#             })
            
#         # 4. Devolve a lista pronta para o Front-end
#         return jsonify(lista_produtos), 200

#     except Exception as e:
#         print(f"Erro ao buscar produtos: {e}")
#         return jsonify({"error": "Falha ao buscar produtos no banco de dados."}), 500