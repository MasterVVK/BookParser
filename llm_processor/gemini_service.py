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

    async def process_chapter(self, chapter_text: str):
        """
        Обрабатывает текст главы через Gemini API.
        :param chapter_text: Текст главы для обработки.
        :return: Обработанный текст или None в случае ошибки.
        """
        params = {"key": GEMINI_API_KEY}
        headers = {"Content-Type": "application/json"}

        system_prompt = (
            "You are tasked with improving a Russian text that has been machine-translated. "
            "The text may contain errors, awkward phrasing, or unnatural language due to the machine translation process. "
            "Your goal is to refine and polish the text to make it sound more natural and fluent in Russian.\n\n"
            "Here is the Russian text that needs improvement:\n\n"
            "<russian_text>\n"
            "{{RUSSIAN_TEXT}}\n"
            "</russian_text>\n\n"
            "Please follow these steps to improve the text..."
        )
        user_prompt = system_prompt.replace("{{RUSSIAN_TEXT}}", chapter_text)

        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}]
        }

        try:
            print("Отправка запроса в Gemini API...")
            print(f"Payload: {payload}")

            response = await self.client.post(self.base_url, headers=headers, params=params, json=payload)
            print(f"HTTP Status: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code == 200:
                data = response.json()
                return data  # Возвращаем весь JSON-ответ для анализа
            else:
                print(f"Ошибка API: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе к Gemini API: {e}")
            return None
        finally:
            await self.client.aclose()