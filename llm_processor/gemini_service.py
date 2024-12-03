import httpx
from httpx_socks import SyncProxyTransport
from config import GEMINI_API_KEY, PROXY_URL

class GeminiService:
    def __init__(self, timeout: int = 30):
        """
        Инициализация сервиса Gemini с поддержкой SOCKS-прокси и пользовательским тайм-аутом.
        :param timeout: Тайм-аут для HTTP-запросов в секундах (по умолчанию 30 секунд).
        """
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY отсутствует. Проверьте файл config.py.")
        if not PROXY_URL:
            raise ValueError("PROXY_URL отсутствует. Проверьте файл config.py.")

        self.api_key = GEMINI_API_KEY
        self.proxy_url = PROXY_URL

        # Настраиваем прокси
        self.transport = SyncProxyTransport.from_url(self.proxy_url)
        self.client = httpx.Client(transport=self.transport, timeout=httpx.Timeout(timeout))

    def process_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.0, max_output_tokens: int = 8000):
        """
        Обрабатывает текст через Gemini API с использованием SOCKS-прокси.
        :param system_prompt: Системный запрос для настройки модели.
        :param user_prompt: Пользовательский текст для обработки.
        :param temperature: Параметр температуры (отвечает за креативность).
        :param max_output_tokens: Максимальное количество токенов в ответе.
        :return: Обработанный текст или None в случае ошибки.
        """
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }

        # Выполняем запрос через httpx клиент
        try:
            response = self.client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "generationConfig": generation_config,
                    "contents": [{"parts": [{"text": system_prompt}, {"text": user_prompt}]}]
                },
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка API: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Ошибка при запросе к Gemini API через прокси: {e}")
            return None
