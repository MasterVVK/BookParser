from database.database_manager import DatabaseManager
from llm_processor.gemini_service import GeminiService

def process_chapters(book_id):
    """
    Обрабатывает все необработанные главы книги через Gemini API.
    :param book_id: ID книги для обработки.
    """
    gemini = GeminiService()

    # Получаем необработанные главы для указанной книги
    unprocessed_chapters = DatabaseManager.get_unprocessed_chapters(book_id=book_id)
    print(unprocessed_chapters)

    if not unprocessed_chapters:
        print("Нет необработанных глав для обработки.")
        return

    for chapter in unprocessed_chapters:
        print(f"Обработка главы {chapter.chapter_number}: {chapter.title}...")

        # Формируем запросы
        system_prompt_path = "system_prompt.txt"  # Путь к файлу с system_prompt
        try:
            with open(system_prompt_path, "r", encoding="utf-8") as file:
                system_prompt = file.read()
        except Exception as e:
            print(f"Не удалось загрузить system_prompt: {e}")
            continue

        user_prompt = f"Here is the Russian text that needs improvement:\n{chapter.content}"

        # Отправляем запрос в Gemini API
        response = gemini.process_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
            max_output_tokens=8000,
        )

        if response:
            # Извлекаем обработанный текст
            processed_content = response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if processed_content:
                # Сохраняем обработанный текст в базу данных
                DatabaseManager.mark_chapter_as_processed(chapter.id, processed_content)
                print(f"Глава {chapter.chapter_number} обработана успешно.")
            else:
                print(f"Ошибка: пустой обработанный текст для главы {chapter.chapter_number}.")
        else:
            print(f"Не удалось обработать главу {chapter.chapter_number}.")

if __name__ == "__main__":
    # Укажите ID книги для обработки
    book_id = 1  # Замените на нужный ID книги
    process_chapters(book_id)
