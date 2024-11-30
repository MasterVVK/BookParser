from parsers.book_parser import BookParser
from database.database_manager import DatabaseManager

if __name__ == '__main__':
    start_url = 'https://wuxiaworld.ru/imperator-syanvu/kontrataka-izgnannogo-uchenika-glava-1-uchenik-sekty/'
    book_title = 'Контратака изгнанного ученика'
    max_chapters = 3  # Указываем максимальное количество глав

    # Список текстов, которые нужно исключить при парсинге
    excluded_texts = [
        'Редактируется Читателями!',
        'Читать»',
        'Автор: Six Circles three',
        'Перевод: Artificial_Intelligence',
        'Нет главы и т.п.',
        'BANISHED DISCIPLE’S COUNTERATTACK'
    ]

    # Сохраняем книгу в базу данных (или обновляем её, если уже существует)
    DatabaseManager.save_book_to_db(book_title, start_url, max_chapters, excluded_texts)

    # Запуск парсинга
    book_parser = BookParser(start_url, book_title, max_chapters=max_chapters)
    book_parser.parse_book()