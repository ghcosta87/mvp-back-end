# ==========================================
# 1. AI CONSTANTS
# ==========================================
GEMINI_MODEL_1 = "gemini-3.1-flash-lite"
GEMINI_MODEL_2 = "gemini-3.6-flash"
GEMINI_MODEL = GEMINI_MODEL_1

GEMINI_MAX_WAITING_TIME= 30000

PROMPT_REV0 ="Extraia a data (DD-MM-YYY) e a lista de produtos com preços unitários finais e suas respectivas marcas tentando dar o nome completo aos produtos."
PROMPT_REV1 ="Extraia a data (DD-MM-YYY) e a lista de produtos com preços unitários finais e suas respectivas marcas tentando dar o nome completo aos produtos. Também extraia o nome do estabelecimento, breve descrição e endereço"
PROMPT_REV2 ="Extraia a data (DD-MM-YYY) e a lista de produtos com preços unitários finais e suas respectivas marcas tentando dar o nome completo aos produtos seguido do respectivo peso ou tamanho quando aplicavel. Também extraia o nome do estabelecimento, breve descrição e endereço"
PROMPT = PROMPT_REV2

ERROR_GEMINI_IMAGE_PROCESS="Erro interno ao processar a imagem com a IA:"
ERROR_GEMINI_WRONG_FORMAT="Você precisa adicionar uma imagem ..."
ERROR_GEMINI_TIMEOUT="O tempo de análise esgotou. Tente enviar novamente."

# ==========================================
# 2. SQL CONSTANTS
# ==========================================
SUCCESS_SQL_PRODUCT_ADD=" produtos salvos com sucesso!"
SUCCESS_SQL_USER_DEL="Usuário deletado com sucesso!"
SUCCESS_SQL_LIST_ADD="Lista criada com sucesso!"
SUCCESS_SQL_LIST_REMOVE="Lista removida"
SUCCESS_SQL_LIST_PRODUCT_DEL="Produtos selecionados foram removidos."
SUCCESS_LOGIN_AUTHORIZED="Login realizado com sucesso"

ERROR_SQL_PRODUCT_ADD="Erro ao adicionar produtos no banco de dados:"

ERROR_SQL_USER_NOT_FOUND="Usuário não encontrado."
ERROR_SQL_USER_DEL="Não foi possível deletar o usuário: "
ERROR_SQL_USER_WRONG_PASSWORD="Senha incorreta."
ERROR_SQL_USER_ALREADY_IN_DATABASE="CPF, E-mail ou Telefone já cadastrados."

ERROR_SQL_LIST_ALREADY_IN_DATABASE="Lista já está cadastrada."
ERROR_SQL_LIST_NOT_FOUND="Lista não encontrada."
ERROR_SQL_LIST_REMOVED="Lista removida."
ERROR_SQL_LIST_PRODUCT_NOT_FOUND="Produto não encontrado na lista."

ERROR_SQL_ADD_FROM_IMAGE="Nenhum produto encontrado."

ERROR_SQL_UNKNOWN="algo estranho aconteceu ..."

# ==========================================
# 3. PROCESSAMENTO DE IMAGEM
# ==========================================
ERROR_EMPTY_IMAGE="Os bytes da imagem estão vazios."
ERROR_EMPTY_FILE="O arquivo enviado está vazio."

# ==========================================
# 4. LOGGER
# ==========================================
IMAGE_NOT_COMPATIBLE="Formato de imagem não compativel."
GEMINI_NOT_RESPONDING="API do Gemini demoroua responder"
PRODUCT_NOT_FOUND="API do Gemini não encontrou nenhum produto"

# ==========================================
# 5. OTHER
# ==========================================
ERRO_INTERNO="Ocorreu um erro interno"