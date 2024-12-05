from parsers.book_parser import BookParser
from database.database_manager import DatabaseManager
from parsers.export_to_epub import export_book_to_epub  # Импорт функции экспорта в EPUB
from database.models import session, Book

if __name__ == '__main__':
    start_url = 'https://wuxiaworld.ru/imperator-syanvu/kontrataka-izgnannogo-uchenika-glava-1-uchenik-sekty/'
    book_title = 'Контратака изгнанного ученика'
    max_chapters = 3365  # Указываем максимальное количество глав

    # Список текстов, которые нужно исключить при парсинге
    excluded_texts = [
        'Редактируется Читателями!',
        'Читать»',
        'Автор: Six Circles three',
        'Перевод: Artificial_Intelligence',
        'Нет главы и т.п.',
        'BANISHED DISCIPLE’S COUNTERATTACK'
    ]

    # Поиск книги по названию
    book = session.query(Book).filter_by(title=book_title).first()
    if not book:
        # Если книга не найдена, создаём новую запись в базе данных
        book = DatabaseManager.save_book_to_db(book_title, start_url, max_chapters, excluded_texts)

    # Запуск парсинга
    book_parser = BookParser(start_url, book_title, max_chapters=max_chapters)
    book_parser.parse_book()

    # Проверка наличия обработанных глав
    processed_chapters = DatabaseManager.get_processed_chapters(book.id) if hasattr(DatabaseManager, 'get_processed_chapters') else []
    #processed_chapters = []
    if processed_chapters:
        print(f'Обработанные главы найдены ({len(processed_chapters)}). Начинается экспорт...')
        # Экспорт обработанных глав в формат EPUB
        export_book_to_epub(book.id)
    else:
        print(f'Для книги "{book_title}" нет обработанных глав. Экспорт не выполнен.')
