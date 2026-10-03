"""
Configuração central do bot.
Carrega variáveis de ambiente do arquivo .env e define caminhos padrão.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# --- WhatsApp Business Cloud API (Meta) ---
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "meu_token_secreto")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v21.0")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")  # opcional, para validar assinatura

# --- Claude (Anthropic) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

# --- Administração ---
ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP", "")
ADMIN_NOME = os.getenv("ADMIN_NOME", "Administrador")

# --- Pagamento (PIX fixo da loja) ---
PIX_CHAVE = os.getenv("PIX_CHAVE", "")
PIX_NOME = os.getenv("PIX_NOME", "")
PIX_BANCO = os.getenv("PIX_BANCO", "")
NOME_LOJA = os.getenv("NOME_LOJA", "Loja de Suplementos")

FRETE_PADRAO = float(os.getenv("FRETE_PADRAO", "15.00"))

# --- Caminhos de dados locais ---
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "banco" / "loja.db")))
COMPROVANTES_DIR = Path(os.getenv("COMPROVANTES_DIR", str(DATA_DIR / "comprovantes")))
PRODUTOS_XLSX = Path(os.getenv("PRODUTOS_XLSX", str(DATA_DIR / "produtos" / "produtos.xlsx")))
LOGS_DIR = Path(os.getenv("LOGS_DIR", str(DATA_DIR / "logs")))
BACKUPS_DIR = Path(os.getenv("BACKUPS_DIR", str(DATA_DIR / "backups")))

for _p in [DB_PATH.parent, COMPROVANTES_DIR, PRODUTOS_XLSX.parent, LOGS_DIR, BACKUPS_DIR]:
    _p.mkdir(parents=True, exist_ok=True)

# --- Servidor Flask ---
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
