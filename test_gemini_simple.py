import asyncio
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

    async def send_simple_request(self):
        """
        Отправляет простой запрос к Gemini API и проверяет наличие ответа.
        """
        params = {"key": GEMINI_API_KEY}
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": "Привет, как ты?"}]}]
        }

        try:
            print("Отправка простого запроса в Gemini API...")
            response = await self.client.post(self.base_url, headers=headers, params=params, json=payload)
            print(f"HTTP Status: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Ошибка API: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе к Gemini API: {e}")
            return None
        finally:
            await self.client.aclose()


async def main():
    gemini_service = GeminiService()
    response = await gemini_service.send_simple_request()

    if response:
        print("Ответ от Gemini API получен:")
        print(response)
    else:
        print("Ответ от Gemini API не получен.")


if __name__ == '__main__':
    asyncio.run(main())
