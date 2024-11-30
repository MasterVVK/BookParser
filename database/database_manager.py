from database.models import Book, Chapter, session

class DatabaseManager:
    """Класс для управления операциями с базой данных."""

    @staticmethod
    def save_book_to_db(book_title, start_url, total_chapters=0):
        """Сохранить книгу в базу данных или обновить её, если она уже существует."""
        book = session.query(Book).filter_by(title=book_title).first()
        if not book:
            book = Book(title=book_title, start_url=start_url, total_chapters=total_chapters)
            session.add(book)
        session.commit()
        return book

    @staticmethod
    def save_chapter_to_db(book, chapter_number, chapter_title, content):
        """Сохранить или обновить главу в базе данных."""
        chapter = session.query(Chapter).filter_by(book_id=book.id, chapter_number=chapter_number).first()
        if chapter:
            # Обновляем существующую главу
            chapter.title = chapter_title
            chapter.content = content
            chapter.processed = False
            chapter.processed_content = None
        else:
            # Создаём новую главу
            chapter = Chapter(
                book_id=book.id,
                chapter_number=chapter_number,
                title=chapter_title,
                content=content,
                status=False
            )
            session.add(chapter)
        session.commit()
        return chapter

    @staticmethod
    def mark_chapter_as_processed(chapter_id, processed_content):
        """Обновить статус главы как обработанной и сохранить обработанный текст."""
        chapter = session.query(Chapter).filter_by(id=chapter_id).first()
        if chapter:
            chapter.processed = True
            chapter.processed_content = processed_content
            session.commit()

    @staticmethod
    def get_unprocessed_chapters():
        """Получить все главы, которые ещё не были обработаны."""
        return session.query(Chapter).filter_by(processed=False).all()
