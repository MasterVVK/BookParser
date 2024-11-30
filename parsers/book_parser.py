from parsers.chapter_parser import ChapterParser
from database.database_manager import DatabaseManager

class BookParser:
    """Класс для парсинга книги."""

    def __init__(self, start_url, book_title, max_chapters=10):
        self.start_url = start_url
        self.book_title = book_title
        self.max_chapters = max_chapters

    def parse_book(self):
        """Парсинг всей книги, начиная с начального URL."""
        # Сохраняем книгу в базу данных
        book = DatabaseManager.save_book_to_db(self.book_title, self.start_url, self.max_chapters)

        # Парсинг глав
        chapter_parser = ChapterParser(self.max_chapters)
        chapter_parser.parse_chapter(self.start_url, book)
