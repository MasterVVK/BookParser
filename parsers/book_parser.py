from parsers.chapter_parser import ChapterParser
from database.database_manager import DatabaseManager

class BookParser:
    """Класс для парсинга книги."""

    def __init__(self, start_url, book_title, max_chapters=10, delay=3):
        self.start_url = start_url
        self.book_title = book_title
        self.max_chapters = max_chapters
        self.delay = delay  # Задержка между запросами

    def parse_book(self):
        """Парсинг всей книги, начиная с начального URL."""
        # Сохраняем книгу в базу данных
        book = DatabaseManager.save_book_to_db(self.book_title, self.start_url, self.max_chapters)

        # Парсинг глав
        current_url = self.start_url
        chapter_parser = ChapterParser(self.max_chapters, self.delay)

        while current_url and chapter_parser.chapter_count < self.max_chapters:
            print(f"Обрабатывается глава {chapter_parser.chapter_count + 1} из {self.max_chapters}...")
            current_url = chapter_parser.parse_chapter(current_url, book)

        print(f'Парсинг книги "{self.book_title}" завершён.')
