from llm_processor.gemini_pro_service import GeminiService
from database.database_manager import DatabaseManager
import time
import os

REQUEST_COUNTER_FILE = "request_counter.txt"
MAX_REQUESTS_PER_MINUTE = 2  # Ограничение на запросы в минуту

def load_request_counter():
    """Загружает время последнего сброса лимита."""
    if os.path.exists(REQUEST_COUNTER_FILE):
        with open(REQUEST_COUNTER_FILE, "r") as file:
            last_reset_time = float(file.read().strip())
            return last_reset_time
    return time.time()

def save_request_counter(last_reset_time):
    """Сохраняет время последнего сброса лимита."""
    with open(REQUEST_COUNTER_FILE, "w") as file:
        file.write(f"{last_reset_time}")

def enforce_minute_limit(last_reset_time, request_count):
    """
    Соблюдает ограничение запросов в минуту.
    """
    current_time = time.time()
    if current_time - last_reset_time < 60 and request_count >= MAX_REQUESTS_PER_MINUTE:
        wait_time = 60 - (current_time - last_reset_time)
        print(f"Достигнут лимит запросов в минуту. Ожидание {wait_time:.2f} секунд.")
        time.sleep(wait_time)
        last_reset_time = time.time()
        request_count = 0
    elif current_time - last_reset_time >= 60:
        # Сбрасываем лимиты, если минута прошла
        last_reset_time = time.time()
        request_count = 0
    return last_reset_time, request_count

def process_chapters(book_id):
    """
    Обработка необработанных глав для указанной книги.
    """
    gemini = GeminiService(timeout=240)
    unprocessed_chapters = DatabaseManager.get_unprocessed_chapters(book_id)
    if not unprocessed_chapters:
        print(f"Нет необработанных глав для книги {book_id}.")
        return

    last_reset_time = load_request_counter()
    request_count = 0

    for chapter in unprocessed_chapters:
        print(f"Обработка главы {chapter.chapter_number}: {chapter.title}...")

        # Соблюдаем ограничение запросов в минуту
        last_reset_time, request_count = enforce_minute_limit(last_reset_time, request_count)

        # Формирование запроса
        with open("system_prompt.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read()

        user_prompt = f"Here is the Russian text that needs improvement:\n{chapter.content}"
        response = gemini.process_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
            max_output_tokens=8000
        )

        if response:
            processed_content = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', None)
            if processed_content:
                DatabaseManager.mark_chapter_as_processed(chapter.id, processed_content)
                print(f"Глава {chapter.chapter_number} обработана.")
            else:
                print(f"Ошибка обработки главы {chapter.chapter_number}.")
        else:
            print(f"Gemini API не вернул ответа для главы {chapter.chapter_number}.")

        # Увеличиваем счётчик запросов и сохраняем время последнего сброса
        request_count += 1
        save_request_counter(last_reset_time)

        # Фиксированная пауза между запросами для стабильности
        time.sleep(1)

if __name__ == "__main__":
    # ID книги для обработки
    BOOK_ID = 1
    try:
        process_chapters(BOOK_ID)
    except RuntimeError as e:
        print(f"Ошибка: {e}")
