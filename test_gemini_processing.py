import asyncio
from llm_processor.gemini_service import GeminiService

async def test_gemini_universal():
    """
    Тест универсального Gemini API с системным и пользовательским запросами.
    """
    gemini_service = GeminiService()

    # Системный запрос
    system_prompt = (
        "You are tasked with improving a Russian text that has been machine-translated. "
        "The text may contain errors, awkward phrasing, or unnatural language due to the machine translation process. "
        "Your goal is to refine and polish the text to make it sound more natural and fluent in Russian."
    )

    # Пользовательский запрос
    user_prompt = "Пример текста для обработки. Здесь могут быть ошибки, которые нужно исправить."

    # Отправляем запрос
    response = await gemini_service.send_request(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.5,
        max_tokens=2000
    )

    if response:
        print("Ответ от Gemini API:")
        print(response)
    else:
        print("Gemini API не вернул ответа.")

if __name__ == '__main__':
    asyncio.run(test_gemini_universal())
