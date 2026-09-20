import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import os

def configurar_logs():
    # 1. Garante que a pasta de logs existe
    # os.makedirs("logs", exist_ok=True)
    log_path = "logs/"
    if not os.path.exists(log_path):
        print("pasta nao existe!")
   # então cria o diretorio
        os.makedirs(log_path)

    # 2. Define o formato universal
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | [%(name)-24s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 3. Handler de Arquivo
    file_handler = RotatingFileHandler(
        "logs/backend.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # 4. Handler de Terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 5. Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG) # Captura absolutamente TUDO
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 6. Filtros Específicos
    logging.getLogger("werkzeug").setLevel(logging.DEBUG) 
    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    logging.getLogger("google.genai").setLevel(logging.DEBUG)
    logging.getLogger("PIL").setLevel(logging.DEBUG)
    
def log_execucao(func):
    """Decorator que loga automaticamente o início e o fim de qualquer função"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # func.__name__ pega o nome exato da função dinamicamente!
        logging.info(f"[{func.__name__}] Iniciando execução...")
        
        resultado = func(*args, **kwargs) # Executa a sua função de verdade
        
        logging.info(f"[{func.__name__}] Execução finalizada com sucesso.")
        return resultado
    return wrapper
