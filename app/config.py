import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
RESUMES_DIR = UPLOAD_DIR / "resumes"
STATIC_DIR = BASE_DIR / "static"

# Criar diretórios se não existirem
for dir_path in [DATA_DIR, RESUMES_DIR, STATIC_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Configurações da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente. Por favor, configure a variável OPENAI_API_KEY no arquivo .env")

# Configurações da aplicação
MINIMUM_SCORE_FOR_NOTIFICATION = 70
SUPPORTED_FILE_TYPES = ["pdf", "docx", "doc"]

# Categorias de vagas
JOB_CATEGORIES = [
    "Desenvolvimento",
    "Dados",
    "DevOps",
    "UX/UI",
    "Produto",
    "Outros"
] 