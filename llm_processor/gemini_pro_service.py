import httpx
from httpx_socks import SyncProxyTransport
from config import GEMINI_API_KEYS, PROXY_URL

class GeminiService:
    def __init__(self, timeout: int = 30):
        if not GEMINI_API_KEYS:
            raise ValueError("GEMINI_API_KEYS отсутствуют. Проверьте файл config.py.")
        if not PROXY_URL:
            raise ValueError("PROXY_URL отсутствует. Проверьте файл config.py.")

        self.api_keys = GEMINI_API_KEYS
        self.current_key_index = 0
        self.proxy_url = PROXY_URL

        # Настраиваем прокси
        self.transport = SyncProxyTransport.from_url(self.proxy_url)
        self.client = httpx.Client(transport=self.transport, timeout=httpx.Timeout(timeout))

    @property
    def current_key(self):
        return self.api_keys[self.current_key_index]

    def switch_to_next_key(self):
        """Переключает на следующий API-ключ."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"Переключение на следующий ключ: GEMINI_API_KEY={self.current_key}")

    def process_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.0, max_output_tokens: int = 8000):
        """Обрабатывает текст через Gemini API с использованием нескольких ключей."""
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
        }

        for _ in range(len(self.api_keys)):  # Попытка использовать все ключи по очереди
            try:
                response = self.client.post(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent",
                    params={"key": self.current_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "generationConfig": generation_config,
                        "contents": [{"parts": [{"text": system_prompt}, {"text": user_prompt}]}],
                    },
                )

                if response.status_code == 200:
                    return response.json()

                elif response.status_code == 429:  # Лимит исчерпан
                    print(f"Ключ {self.current_key} исчерпан. Переключение на следующий ключ.")
                    self.switch_to_next_key()

                elif response.status_code == 400 and "API_KEY_INVALID" in response.text:
                    print(f"Ошибка API: Неверный ключ {self.current_key}. Скрипт остановлен.")
                    exit(1)  # Завершение работы при ошибке ключа

                else:
                    print(f"Ошибка API: {response.status_code} - {response.text}")
                    return None

            except Exception as e:
                print(f"Ошибка при запросе: {e}")
                return None

        print("Все API-ключи исчерпаны или недействительны.")
        return None
