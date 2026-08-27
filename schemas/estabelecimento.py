# from pydantic import BaseModel
# from typing import Optional, List
# from model.estabelecimento import Estabelecimento

# from datetime import datetime

# # from schemas import ComentarioSchema

# class EstabelecimentoSchema(BaseModel):
#     """ Define como um novo estabelecimento a ser inserido deve ser representado
#     """
#     nome: str = "Pão de Açucar"
#     descricao: str = "alguma coisa"
#     endereco: str = "Rio de Janeiro"
#     estabelecimento: int = 1
#     data_de_cadastro = datetime.now()
    
# class EstabelecimentoBuscaSchema(BaseModel):
#     """ Define como deve ser a estrutura que representa a busca. Que será
#         feita apenas com base no nome do usuário.
#     """
#     nome: str = "Pão de Açucar"
    
# class ListagemEstabelecimentosSchema(BaseModel):
#     """ Define como uma listagem de usuários será retornada.
#     """
#     nome: List[EstabelecimentoSchema]
    
# def apresenta_estabelecimento(estabelecimento: Estabelecimento):
#     """ Retorna uma representação do estabelecimento seguindo o schema definido em
#         EstabelecimentoViewSchema.
#     """
#     return {
#             "nome": estabelecimento.nome,
#             "descricao": estabelecimento.descricao,
#             "endereco": estabelecimento.endereco,
#             "estabelecimento": estabelecimento.estabelecimento,
#             "data_de_cadastro": estabelecimento.data_de_cadastro.isoformat()
#     }
    
    