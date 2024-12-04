import time
import os
import httpx
from llm_processor.gemini_pro_service import GeminiService
from database.database_manager import DatabaseManager

# Настройки лимитов
MAX_REQUESTS_PER_MINUTE = 2
MAX_TOKENS_PER_MINUTE = 32000
MAX_REQUESTS_PER_DAY = 50
REQUEST_COUNTER_FILE = "request_counter.txt"

def enforce_rate_limits(tokens_used, last_reset_time, daily_requests):
    """
    Управление лимитами API (запросы и токены).
    :param tokens_used: Количество токенов, использованных за текущую минуту.
    :param last_reset_time: Время последнего сброса лимитов.
    :param daily_requests: Текущее количество запросов за сутки.
    :return: Обновлённое количество токенов, время последнего сброса и дневной счётчик запросов.
    """
    current_time = time.time()

    # Сброс лимитов раз в минуту
    if current_time - last_reset_time >= 60:
        tokens_used = 0
        last_reset_time = current_time

    # Сброс лимита запросов раз в сутки
    if daily_requests >= MAX_REQUESTS_PER_DAY:
        raise RuntimeError("Достигнут лимит запросов в сутки (50). Попробуйте снова завтра.")

    return tokens_used, last_reset_time, daily_requests

def load_request_counter():
    """
    Загружает дневной счётчик запросов из файла. Если файл не найден, создаёт новый.
    """
    if os.path.exists(REQUEST_COUNTER_FILE):
        with open(REQUEST_COUNTER_FILE, "r") as file:
            timestamp, daily_requests = file.read().strip().split(",")
            return float(timestamp), int(daily_requests)
    else:
        return time.time(), 0

def save_request_counter(timestamp, daily_requests):
    """
    Сохраняет дневной счётчик запросов в файл.
    """
    with open(REQUEST_COUNTER_FILE, "w") as file:
        file.write(f"{timestamp},{daily_requests}")

def process_chapters(book_id):
    """
    Обработка необработанных глав для указанной книги.
    :param book_id: ID книги.
    """
    gemini = GeminiService(timeout=60)  # Увеличенный тайм-аут

    # Получаем необработанные главы
    unprocessed_chapters = DatabaseManager.get_unprocessed_chapters(book_id)

    if not unprocessed_chapters:
        print(f"Нет необработанных глав для книги с ID {book_id}.")
        return

    tokens_used = 0
    last_reset_time = time.time()

    # Загружаем дневной счётчик запросов
    last_day_reset, daily_requests = load_request_counter()

    for chapter in unprocessed_chapters:
        # Проверяем, нужно ли сбросить дневной счётчик
        if time.time() - last_day_reset >= 86400:  # 24 часа
            daily_requests = 0
            last_day_reset = time.time()

        # Применяем лимиты
        tokens_used, last_reset_time, daily_requests = enforce_rate_limits(
            tokens_used, last_reset_time, daily_requests
        )

        print(f"Обработка главы {chapter.chapter_number}: {chapter.title}...")

        # Загрузка системного запроса из файла
        with open("system_prompt.txt", "r", encoding="utf-8") as file:
            system_prompt = file.read()

        # Формирование пользовательского запроса
        user_prompt = f"Here is the Russian text that needs improvement:\n{chapter.content}"

        # Подсчет токенов для текущего запроса
        current_tokens = len(system_prompt.split()) + len(user_prompt.split())
        tokens_used += current_tokens

        # Отправляем запрос в Gemini
        response = None
        try:
            response = gemini.process_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.0,
                max_output_tokens=8000
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print("Ошибка API: Достигнут лимит запросов. Скрипт остановлен.")
                exit(1)  # Завершаем выполнение
            else:
                print(f"HTTP ошибка {e.response.status_code}: {e.response.text}")
                continue
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            continue

        if response:
            # Получаем обработанный текст
            processed_content = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', None)
            if processed_content:
                print(f"Глава {chapter.chapter_number} обработана.")
                DatabaseManager.mark_chapter_as_processed(chapter.id, processed_content)
                daily_requests += 1
                save_request_counter(last_day_reset, daily_requests)  # Обновляем счётчик запросов
            else:
                print(f"Не удалось обработать главу {chapter.chapter_number}.")
        else:
            print(f"Gemini API не вернул ответа для главы {chapter.chapter_number}.")

        # Применяем ограничение на количество запросов в минуту
        wait_time = max(0, 60 - (time.time() - last_reset_time))  # Убедиться, что wait_time >= 0
        if wait_time > 0:
            print(f"Достигнут лимит запросов в минуту. Ожидание {wait_time:.2f} секунд.")
            time.sleep(wait_time)

        # Фиксированная пауза между запросами
        time.sleep(5)

if __name__ == "__main__":
    # ID книги для обработки
    BOOK_ID = 2
    try:
        process_chapters(BOOK_ID)
    except RuntimeError as e:
        print(f"Ошибка лимита: {e}")
