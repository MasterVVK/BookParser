import asyncio
from database.database_manager import DatabaseManager
from llm_processor.gemini_service import GeminiService
from database.models import session, Book

async def process_unprocessed_chapters(book_title):
    """
    Обрабатывает все необработанные главы книги через Gemini API.
    :param book_title: Название книги.
    """
    # Найти книгу по названию
    book = session.query(Book).filter_by(title=book_title).first()
    if not book:
        print(f"Книга с названием '{book_title}' не найдена.")
        return

    # Получить необработанные главы
    chapters = DatabaseManager.get_unprocessed_chapters()
    if not chapters:
        print(f"Все главы книги '{book_title}' уже обработаны.")
        return

    gemini_service = GeminiService()

    for chapter in chapters:
        print(f"Обработка главы {chapter.chapter_number}: {chapter.title}...")
        processed_content = await gemini_service.process_chapter(chapter.content)

        if processed_content:
            DatabaseManager.mark_chapter_as_processed(chapter.id, processed_content)
            print(f"Глава {chapter.chapter_number} успешно обработана.")
        else:
            print(f"Не удалось обработать главу {chapter.chapter_number}.")

if __name__ == '__main__':
    # Укажите название книги для теста
    book_title = "Контратака изгнанного ученика"
    asyncio.run(process_unprocessed_chapters(book_title))
