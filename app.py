APP_VERSION = "v2.0.0-beta"
# ==========================================
# 1. BIBLIOTECAS NATIVAS DO PYTHON
# ==========================================
import os
import io
import logging
from logger import configurar_logs, log_execucao
from service.listas import check_duplicate, return_error
from sqlalchemy import JSON, func
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
from model.lista import ListaDeCompras, ListaDeItens
from model.usuarios import Usuario
from model.estabelecimento import Estabelecimento

# Schemas (Validação de Dados)
from schemas.usuarios import UsuarioSchema, UsuarioBuscaSchema, apresenta_usuario
from schemas.produto import (
    CupomExtraidoSchema,
    ProductNotFoundSchema,
    ProdutoSchema,
    ConsultaSchema,
    ProductUpdateReplySchema,
    ProductReplySchema,
)
from schemas.listas import (
    ApagarItemDaLista,
    AddListReplySchema,
    ListReplySchema,
    BuscarListaDeCompras,
    CriarListaDeComprasSchema,
    ListaDeComprasSchema,
    ProdutoAdicionadoNaLista,
    ListErrorSchema,
)
from schemas.upload import UploadSchema
from schemas.error import ErrorSchema, ErrorUploadSchema

# ==========================================
# 2. DEFINIÇÃO DAS HOME TAGS
# ==========================================
tag_user = Tag(name="Usuários", description="Funções de controle de usuários")
tag_image = Tag(
    name="Imagens", description="Funções de upload e processamento de imagens"
)
tag_produtos = Tag(name="Produtos", description="Funções de listagem de produtos")
tag_home = Tag(
    name="Home", description="Função de redirecionamento para a documentação da API"
)
tag_listas = Tag(
    name="Listas", description="Função de mansipulação das listas de compras"
)
tag_dev = Tag(
    name="Desenvolvimento", description="Área de testes e desenvolvimento de rotas"
)

# ==========================================
# 3. CONFIGURAÇÕES GLOBAIS
# ==========================================

configurar_logs()
logging.info("\n\n")

load_dotenv(find_dotenv())
chave_api = os.getenv("API_KEY")

register_heif_opener()  # Liga o suporte a HEIC dentro do Pillow

info = Info(title="Minha API", version="0.0.1")
app = OpenAPI(__name__, info=info)
CORS(app)

#####################################
######## 1. Manipulação de Usuários
####


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
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.post(
    "/deletar_usuario",
    tags=[tag_user],
    responses={
        HTTPStatus.OK: UsuarioSchema,
        HTTPStatus.BAD_REQUEST: ErrorSchema,  # somente se o tiver problemas na base de dados
        HTTPStatus.UNAUTHORIZED: ErrorSchema,  # erro de senha
        HTTPStatus.NOT_FOUND: ErrorSchema,  # somente se o usuario forçar o login
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
            return {
                "message": const.ERROR_SQL_USER_WRONG_PASSWORD
            }, HTTPStatus.UNAUTHORIZED

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.post(
    "/login",
    tags=[tag_user],
    responses={
        HTTPStatus.OK: UsuarioSchema,
        HTTPStatus.BAD_REQUEST: ErrorSchema,
        HTTPStatus.UNAUTHORIZED: ErrorSchema,
        HTTPStatus.NOT_FOUND: ErrorSchema,
    },
)
def logar(form: UsuarioBuscaSchema):
    """Verifica se o usuário existe e se a senha está correta e retorna uma mensagem de sucesso ou erro."""
    # logging.info("Email recebido")
    # logging.info(form.email)
    try:
        session = Session()
        usuario_encontrado = session.query(Usuario).filter_by(email=form.email).first()

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
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


#####################################
######## 3. Manipulação de Imagem
####


@app.post(
    "/upload",
    tags=[tag_image],
    responses={
        HTTPStatus.OK: UploadSchema,
        HTTPStatus.LENGTH_REQUIRED: ErrorUploadSchema,
        HTTPStatus.UNSUPPORTED_MEDIA_TYPE: ErrorSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorUploadSchema,
        HTTPStatus.GATEWAY_TIMEOUT: ErrorUploadSchema,
    },
)
def upload_imagem(form: UploadSchema):  # <?> rever e limpar comentarios
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
                http_options=HttpOptions(timeout=const.GEMINI_MAX_WAITING_TIME),
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
        return return_error(ErrorSchema, e, session)

    # 2. SALVAMENTO NO BANCO DE DADOS
    session = Session()
    produtos_salvos = []

    try:
        if "loja" in dados:
            loja_dados = dados["loja"]
            lojaDuplicada = (
                session.query(Estabelecimento)
                .filter_by(endereco=loja_dados["endereco"])
                .first()
            )
            if not lojaDuplicada:
                loja = Estabelecimento(
                    loja_dados["nome"],
                    loja_dados["descricao"],
                    loja_dados["endereco"],
                )
                session.add(loja)

        for item in dados["produtos"]:
            produto = Produto(
                nome=item["nome"],
                marca=item.get("marca", "Sem marca"),
                data_da_compra=item.get("data", datetime.now()),
                preco=item["preco"],
            )
            session.add(produto)
            produtos_salvos.append(produto.nome)

        if not len(produtos_salvos):
            logging.error(const.PRODUCT_NOT_FOUND)
            return {
                "status": "erro",
                "message": f"{len(produtos_salvos)} {const.ERROR_SQL_ADD_FROM_IMAGE}",
                "arquivo": file.filename,
            }, HTTPStatus.LENGTH_REQUIRED

        session.commit()
        return {
            "status": "sucesso",
            "message": f"{len(produtos_salvos)} {const.SUCCESS_SQL_PRODUCT_ADD}",
            "produtos_extraidos": dados["produtos"],
        }, HTTPStatus.OK

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


#####################################
######## 4. Manipulação de Listas
####


@app.post(
    "/buscar_lista_de_compra",
    tags=[tag_listas],
    responses={
        HTTPStatus.OK: ListReplySchema,
        HTTPStatus.NOT_FOUND: ErrorSchema,
    },
)
def buscar_lista_de_compra(form: BuscarListaDeCompras):
    """
    Busca os itens de uma lista de compras
    """
    logging.info("inicio da funcao < buscar_lista_de_compra >")
    logging.debug(f"form.titulo: {form.titulo}")
    session = Session()
    try:
        # 1. Verifica se a lista existe
        query_lista_de_compras = (
            session.query(ListaDeCompras).filter_by(titulo=form.titulo).first()
        )
        if not query_lista_de_compras:
            return {"message": const.ERROR_SQL_LIST_NOT_FOUND}, HTTPStatus.NOT_FOUND

        outputValue = {
            form.titulo: [
                {
                    "nome": item.produto.nome,
                    "marca": item.produto.marca,
                    "quantidade": item.quantidade,
                }
                for item in query_lista_de_compras.itens
            ]
        }

        return ListReplySchema(), HTTPStatus.OK

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()
        logging.info("concluida a funcao < buscar_lista_de_compra >")


############################
######## → Rotas em teste
####


@app.get(
    "/ver_produtos_cadastrados",
    tags=[tag_dev],
    responses={
        HTTPStatus.OK: ConsultaSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
def ver_produtos_cadastrados():
    """
    Retorna todos os produtos da tabela produtos
    """
    try:
        session = Session()

        lista_produtos = [
            {
                "id": produto.id,
                "nome": produto.nome,
                "data_da_compra": produto.data_da_compra,
                "preco": float(produto.preco),
            }
            for produto in session.query(Produto).all()
        ]

        return {"produtos": lista_produtos}, HTTPStatus.OK

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.post(
    "/cadastrar_produto",
    tags=[tag_dev],
    responses={
        HTTPStatus.OK: ConsultaSchema,
        HTTPStatus.CONFLICT: ErrorSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
def cadastrarProdutos(form: CriarListaDeComprasSchema):
    """
    Cria uma lista de compras
    """
    session = Session()
    try:
        duplicateList = (
            session.query(ListaDeCompras).filter_by(titulo=form.titulo).first()
        )

        if duplicateList:
            return {
                "message": const.ERROR_SQL_LIST_ALREADY_IN_DATABASE
            }, HTTPStatus.CONFLICT

        lista = ListaDeCompras(form.titulo)
        session.add(lista)
        session.commit()

        return {"message": const.SUCCESS_SQL_LIST_ADD}, HTTPStatus.OK

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


# ==========================================
# 1. SWAGGER E CONTROLE DE VERSÃO
# ==========================================


@app.get("/", tags=[tag_home])
@log_execucao
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")


@app.get("/version", tags=[tag_home])
@log_execucao
def get_version():
    """
    Carrega a versão do backend
    """
    return {"version": APP_VERSION}, HTTPStatus.OK


# ==========================================
# 5. MANIPULAÇÃO DE PRODUTOS
# ==========================================


@app.get(
    "/produtos",
    tags=[tag_produtos],
    responses={
        HTTPStatus.OK: ConsultaSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
@log_execucao
def listar_produtos():
    """
    Retorna todos os produtos cadastrados no banco de dados
    """
    try:
        session = Session()
        lista_produtos = [
            {
                "id": produto.id,
                "nome": produto.nome,
                "marca": produto.marca,
                "data_da_compra": produto.data_da_compra,
                "preco": produto.preco,
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
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.post(
    "/add_product",
    tags=[tag_produtos],
    responses={
        HTTPStatus.OK: ListReplySchema,
        HTTPStatus.NOT_FOUND: ProductNotFoundSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
@log_execucao
def add_product(form: ProdutoSchema):
    """
    Update a single product information
    """

    logging.debug(f"form recebida: {form}")
    session = Session()
    try:

        product = Produto(
            nome=form.nome,
            marca=form.marca,
            data_da_compra=form.data_da_compra,
            preco=form.preco,
        )

        session.add(product)
        session.commit()

        return (
            ProductReplySchema(
                nome=form.nome,
                marca=form.marca,
                preco=form.preco,
                data_da_compra=form.data_da_compra,
                message=const.SUCCESS_SQL_PRODUCT_ADD,
            ).model_dump(),
            HTTPStatus.OK,
        )

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.put(
    "/update_product_info",
    tags=[tag_produtos],
    responses={
        HTTPStatus.OK: ListReplySchema,
        HTTPStatus.NOT_FOUND: ProductNotFoundSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
@log_execucao
def update_product_info(form: ProductUpdateReplySchema):
    """
    Update a single product information
    """

    logging.debug(f"form recebida: {form}")
    session = Session()
    try:

        product_query = session.query(Produto).filter_by(nome=form.nome_antigo).all()
        if not product_query:
            return (
                ProductNotFoundSchema(
                    message=const.ERROR_SQL_PRODUCT_NOT_FOUND,
                    product_name=str(form.nome),
                ).model_dump(),
                HTTPStatus.NOT_FOUND,
            )

        for item in product_query:
            item.nome = form.nome
            item.marca = form.marca
            item.preco = form.preco
            # product_query.data_da_compra = form.data_da_compra

        session.commit()

        return (
            ProductUpdateReplySchema(
                nome_antigo=form.nome_antigo,
                nome=form.nome,
                marca=form.marca,
                preco=form.preco,
                data_da_compra=form.data_da_compra,
                message=const.SUCCESS_SQL_PRODUCT_UPADTE,
            ).model_dump(),
            HTTPStatus.OK,
        )
    except Exception as e:
        session.rollback()
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


# ==========================================
# 6. MANIPULAÇÃO DE LISTAS
# ==========================================


@app.post(
    "/criar_lista_de_compras",
    tags=[tag_listas],
    responses={
        HTTPStatus.OK: ListReplySchema,
        HTTPStatus.CONFLICT: ListErrorSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
@log_execucao
def criar_lista_de_compras(form: CriarListaDeComprasSchema):
    """
    Cria uma lista de compras
    """
    logging.debug(f"form recebida: {form}")
    session = Session()
    try:
        query = session.query(ListaDeCompras).filter_by(titulo=form.titulo).first()

        if query:
            logging.debug(f"A lista ja existe")
            return (
                ListErrorSchema(
                    message=const.ERROR_SQL_LIST_ALREADY_IN_DATABASE
                ).model_dump(),
                HTTPStatus.CONFLICT,
            )

        lista = ListaDeCompras(titulo=form.titulo)
        session.add(lista)
        session.commit()
        return (
            ListReplySchema(message=const.SUCCESS_SQL_LIST_ADD).model_dump(),
            HTTPStatus.OK,
        )
    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.post(
    "/apagar_lista_de_compras",
    tags=[tag_listas],
    responses={
        HTTPStatus.OK: ListReplySchema,
        HTTPStatus.NOT_FOUND: ListErrorSchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
@log_execucao
def apagar_lista_de_compras(form: BuscarListaDeCompras):
    """
    Apaga a lista de compras
    """
    logging.debug(f"form recebida: {form}")
    session = Session()
    try:
        query_lista_de_compras = (
            session.query(ListaDeCompras).filter_by(titulo=form.titulo).first()
        )
        if not query_lista_de_compras:
            logging.info(f"a lista de compras {form.titulo} não foi encontrada")
            return (
                ListErrorSchema(message=const.ERROR_SQL_LIST_NOT_FOUND).model_dump(),
                HTTPStatus.NOT_FOUND,
            )

        session.delete(query_lista_de_compras)
        session.commit()
        return (
            ListReplySchema(message=const.SUCCESS_SQL_LIST_REMOVE).model_dump(),
            HTTPStatus.OK,
        )

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.post(
    "/adicionar_item_a_lista",
    tags=[tag_listas],
    responses={
        HTTPStatus.OK: AddListReplySchema,
        HTTPStatus.NOT_FOUND: ListReplySchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
@log_execucao
def adicionar_item_a_lista(body: ListaDeComprasSchema):
    """
    Adiciona itens a lista de compra
    """
    logging.debug(f"body: {body}")
    session = Session()
    try:
        # 1. guarda o row da lista selecionada
        query_lista_de_compras = (
            session.query(ListaDeCompras).filter_by(titulo=body.titulo).first()
        )
        # 2. verifica se ela existe
        if not query_lista_de_compras:
            return (
                ListReplySchema(message=const.ERROR_SQL_LIST_NOT_FOUND).model_dump(),
                HTTPStatus.NOT_FOUND,
            )
        # 3. guarda todos os produtos da lista selecionada em um dicionario?
        produtos_listados = [
            item.produto.nome.lower() for item in query_lista_de_compras.itens
        ]
        logging.debug(f"produtos_listados: {produtos_listados}")

        # 4. transforma o form dos itens em uma array de objetos
        item_tmp = [
            {
                "nome": item.nome,
                "marca": item.marca,
                "quantidade": item.quantidade,
                "preco_medio": item.preco_medio,
            }
            for item in body.itens
        ]
        logging.debug(f"item_tmp: {item_tmp}")

        # 5. seleciona para adicionar os que nao estão na lista
        itens_novos_para_adicionar = [
            newItem
            for newItem in item_tmp
            if newItem["nome"].lower() not in produtos_listados
        ]
        logging.debug(f"itens_novos_para_adicionar: {itens_novos_para_adicionar}")

        # 6. ?
        nomes_para_buscar = [
            newItem["nome"].lower()
            for newItem in itens_novos_para_adicionar
            # if newItem["nome"].lower() not in produtos_listados
        ]

        novosItensTotal = len(nomes_para_buscar)
        novosItensTotal = len(itens_novos_para_adicionar)
        itensNaoAdicionados = len(produtos_listados) - len(itens_novos_para_adicionar)

        if not itens_novos_para_adicionar:
            return {
                "message": "Nenhum item novo adicionado (todos já existiam).",
                "addedQuantity": 0,
                "quantityNotAdded": itensNaoAdicionados,
            }, HTTPStatus.OK

        produtos_no_banco = session.query(Produto).filter(
            func.lower(Produto.nome).in_(nomes_para_buscar)
        )
        logging.debug(f"produtos_no_banco: {produtos_no_banco}")

        mapa_produtos = {p.nome.lower(): p.id for p in produtos_no_banco}

        logging.debug(f"mapa_produtos: {mapa_produtos}")

        # 4. Adiciona somente os que não estão repetidos
        for x in item_tmp:
            logging.debug(x)
            lookupName = x["nome"].lower()
            if lookupName in produtos_listados:
                logging.debug(f"produto {x['nome'].lower()} ja esta na lista")

            else:
                logging.debug(f"produto {x['nome'].lower()} sera incluido na lista")
                session.add(
                    ListaDeItens(
                        quantidade=x["quantidade"],
                        lista_id=query_lista_de_compras.id,
                        produto_id=mapa_produtos.get(lookupName),
                    )
                )
        session.commit()
        #  return (AddListReplySchema(message=const.SUCCESS_SQL_LIST_ADD,
        #                                addedQuantity=novosItensTotal,
        #                                quantityNotAdded=itensNaoAdicionados)
        #             .model_dump(), HTTPStatus.OK)
        return {
            "message": const.SUCCESS_SQL_LIST_ADD,
            "addedQuantity": novosItensTotal,
            "quantityNotAdded": itensNaoAdicionados,
        }, HTTPStatus.OK

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()


@app.post(
    "/apagar_item_da_lista",
    tags=[tag_listas],
    responses={
        HTTPStatus.OK: ListReplySchema,
        HTTPStatus.NOT_FOUND: ListReplySchema,
        HTTPStatus.INTERNAL_SERVER_ERROR: ErrorSchema,
    },
)
@log_execucao
def apagar_item_da_lista(form: ApagarItemDaLista):
    """
    Apaga itens da lista de compras
    """
    logging.debug(f"form: {form}")
    session = Session()
    try:
        query_lista = (
            session.query(ListaDeCompras).filter_by(titulo=form.titulo).first()
        )
        if not query_lista:
            return (
                ListReplySchema(message=const.ERROR_SQL_LIST_NOT_FOUND).model_dump(),
                HTTPStatus.NOT_FOUND,
            )

        lista_para_apagar = [item.nome.lower() for item in form.itens]
        logging.debug(f"lista_para_apagar: {lista_para_apagar}")

        pegar_ids_dos_produtos = (
            session.query(Produto.id)
            .filter(func.lower(Produto.nome).in_(lista_para_apagar))
            .all()
        )
        ids_dos_produtos = [item.id for item in pegar_ids_dos_produtos]
        logging.debug(f"ids_dos_produtos: {ids_dos_produtos}")

        linhas_apagadas = (
            session.query(ListaDeItens)
            .filter(
                ListaDeItens.lista_id == query_lista.id,
                ListaDeItens.produto_id.in_(ids_dos_produtos),
            )
            .delete(synchronize_session=False)
        )

        if linhas_apagadas == 0:
            return (
                ListReplySchema(
                    message=const.ERROR_SQL_LIST_PRODUCT_NOT_FOUND
                ).model_dump(),
                HTTPStatus.NOT_FOUND,
            )

        session.commit()

        return (
            ListReplySchema(message=const.SUCCESS_SQL_LIST_PRODUCT_DEL).model_dump(),
            HTTPStatus.OK,
        )

    except Exception as e:
        return return_error(ErrorSchema, e, session)

    finally:
        session.close()
