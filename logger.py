import logging
from logging.handlers import RotatingFileHandler
import os

# Garante que a pasta de logs existe
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# Formato: data/hora, nível, mensagem
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Salva em arquivo, rotacionando quando passar de 5MB (evita arquivo gigante)
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Também mostra no terminal, como você já tem hoje
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)