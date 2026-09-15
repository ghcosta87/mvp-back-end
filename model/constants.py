# ==========================================
# . AI CONSTANTS
# ==========================================
GEMINI_MODEL_1 = "gemini-3.1-flash-lite"
GEMINI_MODEL_2 = "gemini-3.6-flash"
GEMINI_MODEL = GEMINI_MODEL_1

PROMPT_REV0 ="Extraia a data (DD-MM-YYY) e a lista de produtos com preços unitários finais e suas respectivas marcas tentando dar o nome completo aos produtos."
PROMPT_REV1 ="Extraia a data (DD-MM-YYY) e a lista de produtos com preços unitários finais e suas respectivas marcas tentando dar o nome completo aos produtos. Também extraia o nome do estabelecimento, breve descrição e endereço"
PROMPT_REV2 ="Extraia a data (DD-MM-YYY) e a lista de produtos com preços unitários finais e suas respectivas marcas tentando dar o nome completo aos produtos seguido do respectivo peso ou tamanho quando aplicavel. Também extraia o nome do estabelecimento, breve descrição e endereço"
PROMPT = PROMPT_REV2

ERROR_GEMINI_IMAGE_PROCESS="Erro interno ao processar a imagem com a IA:"

# ==========================================
# . SQL CONSTANTS
# ==========================================
SUCCESS_SQL_PRODUCT_ADD=" produtos salvos com sucesso!"
SUCCESS_SQL_USER_DEL="Usuário deletado com sucesso!"

ERROR_SQL_PRODUCT_ADD="Erro ao adicionar produtos no banco de dados:"

ERROR_SQL_USER_NOT_FOUND="Usuário não encontrado."
ERROR_SQL_USER_DEL="Não foi possível deletar o usuário: "
ERROR_SQL_USER_WRONG_PASSWORD="Senha incorreta."


# ==========================================
# .
# ==========================================
ERROR_EMPTY_IMAGE="Os bytes da imagem estão vazios."
ERROR_EMPTY_FILE="O arquivo enviado está vazio."