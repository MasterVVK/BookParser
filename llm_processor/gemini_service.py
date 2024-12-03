import httpx
from httpx_socks import AsyncProxyTransport
from config import GEMINI_API_KEY, PROXY_URL

class GeminiService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY отсутствует. Проверьте файл .env.")

        if not PROXY_URL:
            raise ValueError("PROXY_URL отсутствует. Проверьте файл .env.")

        self.transport = AsyncProxyTransport.from_url(PROXY_URL)
        self.client = httpx.AsyncClient(transport=self.transport)

        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    async def send_request(self, system_prompt: str, user_prompt: str, temperature: float = 0.0, max_tokens: int = 8000):
        """
        Отправляет запрос в Gemini API.
        :param system_prompt: Системный запрос для настройки модели.
        :param user_prompt: Пользовательский запрос (текст, требующий обработки).
        :param temperature: Параметр температуры (отвечает за креативность).
        :param max_tokens: Максимальное количество токенов в ответе.
        :return: Обработанный текст или None в случае ошибки.
        """
        params = {"key": GEMINI_API_KEY}
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": system_prompt}, {"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        try:
            print("Отправка запроса в Gemini API...")
            print(f"Payload: {payload}")

            response = await self.client.post(self.base_url, headers=headers, params=params, json=payload)
            print(f"HTTP Status: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        processed_text = parts[0].get("text", "").strip()
                        return processed_text
                print("Ошибка: Не удалось получить обработанный текст из ответа.")
            else:
                print(f"Ошибка API: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Ошибка при запросе к Gemini API: {e}")
        finally:
            await self.client.aclose()

        return None
