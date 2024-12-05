import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY_URL = os.getenv("PROXY_URL")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEYS = os.getenv("GEMINI_API_KEYS").split(",")
DATABASE_URL = "sqlite:///books.db"  # Можно использовать любую СУБД
MAX_CHAPTERS = 1  # Количество глав для парсинга

