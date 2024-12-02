import httpx
from httpx_socks import AsyncProxyTransport
from config import GEMINI_API_KEY, PROXY_URL

class GeminiService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY отсутствует. Проверьте файл .env.")

        if not PROXY_URL:
            raise ValueError("PROXY_URL отсутствует. Проверьте файл .env.")

        # Настройка транспорта для использования SOCKS5-прокси
        self.transport = AsyncProxyTransport.from_url(PROXY_URL)
        # Создание асинхронного клиента с прокси
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

        # Формируем запрос с подстановкой текста главы
        system_prompt = (
            "You are tasked with improving a Russian text that has been machine-translated. "
            "The text may contain errors, awkward phrasing, or unnatural language due to the machine translation process. "
            "Your goal is to refine and polish the text to make it sound more natural and fluent in Russian.\n\n"
            "Here is the Russian text that needs improvement:\n\n"
            "<russian_text>\n"
            "{{RUSSIAN_TEXT}}\n"
            "</russian_text>\n\n"
            "Please follow these steps to improve the text:\n\n"
            "1. Read through the entire text carefully to understand the context and content.\n"
            "2. Identify and correct any grammatical errors, including issues with case endings, verb aspects, "
            "or agreement between words.\n"
            "3. Improve the sentence structure where necessary to make it more natural in Russian. "
            "This may involve reordering words or breaking long sentences into shorter ones.\n"
            "4. Replace any awkward or unnatural phrases with more idiomatic Russian expressions.\n"
            "5. Ensure that the vocabulary used is appropriate and accurate for the context. "
            "If you encounter any words that seem out of place or incorrectly used, replace them with more suitable alternatives.\n"
            "6. Pay attention to the proper use of Russian punctuation, including the correct placement of commas, dashes, "
            "and quotation marks according to Russian punctuation rules.\n"
            "7. Maintain the original meaning and tone of the text while making it sound more fluent and native-like.\n"
            "8. Be cautious not to introduce elements of other languages or cultures that wouldn't be natural in a Russian text.\n"
            "9. Preserve HTML and EPUB markup\n\n"
            "After making these improvements, provide only the corrected version of the text.\n\n"
            "Remember to maintain the integrity of the Russian language throughout the process. "
            "Do not translate the text into other languages, add explanations, or output technical information. "
            "The goal is to get a polished, natural-sounding Russian text that reads as if it was originally written by a native Russian speaker."
        )
        user_prompt = chapter_text.replace("{{RUSSIAN_TEXT}}", chapter_text)

        payload = {
            "contents": [{
                "parts": [
                    {"text": system_prompt},
                    {"text": user_prompt}
                ]
            }]
        }

        try:
            # Выполнение асинхронного запроса к Gemini API
            response = await self.client.post(self.base_url, headers=headers, params=params, json=payload)

            if response.status_code == 200:
                data = response.json()
                # Распаковка содержимого ответа
                candidates = data.get("candidates", [])
                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        processed_text = parts[0].get("text", "").strip()
                        return processed_text
                print("Ошибка: Не удалось получить обработанный текст из ответа.")
                return None
            else:
                print(f"Ошибка при запросе: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе к Gemini API: {e}")
            return None
        finally:
            await self.client.aclose()  # Закрытие клиента
