"""
Imported libraries
"""

import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types
from PIL import Image
from model import Produto

# Importa as classes criadas no Passo 2
# Arquivo: prompt.py
# 1. Carrega as informações do arquivo .env para a memória do Python
"""
Load enviromental variables
"""
load_dotenv("./.env")
chave_api = os.getenv("API_KEY")
if not chave_api:
    raise ValueError("A chave API_KEY não foi encontrada no arquivo .env!")
load_dotenv(find_dotenv())
chave_api = os.getenv("API_KEY")  # genai.configure(api_key=chave_api)

# Inicializa o cliente da IA
client = genai.Client(api_key=chave_api)

# def processar_imagem_cupom(caminho_imagem: str) -> LeituraNotaFiscal:
def processar_imagem(caminho_imagem: str) -> Produto:
    # Carrega a imagem da nota fiscal/etiqueta
    imagem = Image.open(caminho_imagem)
    prompt = """
    Analise esta imagem de nota fiscal ou etiqueta de produto.
    Extraia o nome do estabelecimento, a data da compra (no formato YYYY-MM-DD) 
    e a lista de todos os produtos com seus respectivos preços unitários finais.
    """
    # 2. Faz a chamada forçando a resposta no schema do Pydantic
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[imagem, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Produto,
            temperature=0.1,  # Baixa temperatura para evitar alucinações de valores
        ),
    )
    # O SDK já converte a resposta para o objeto Pydantic validado
    dados_estruturados: Produto = response.parsed
    return dados_estruturados

# 1 cadastra estabelicimeto, se existir vai direto pro proximo

# 2 cadastra produtos

# --- Exemplo de Uso --
if __name__ == "__main__":
    resultado = processar_imagem_cupom("cupom_fiscal.jpg")
    print(f"Estabelecimento: {resultado.estabelecimento}")
    print(f"Data: {resultado.data_compra}")
    print("-" * 30)
    # Prontos para iterar e fazer os INSERTS na sua tabela SQL!
    for item in resultado.itens:
        print(f"Produto: {item.nome_produto} | Preço: R$ {item.preco:.2f}")
