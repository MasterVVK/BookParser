from sqlalchemy.orm import sessionmaker
from database.models import Book, Chapter, engine

Session = sessionmaker(bind=engine)
session = Session()

class DatabaseManager:
    """Класс для работы с базой данных."""

    @staticmethod
    def save_book_to_db(book_title, start_url, total_chapters=0):
        book = session.query(Book).filter_by(title=book_title).first()
        if not book:
            book = Book(title=book_title, start_url=start_url, total_chapters=total_chapters)
            session.add(book)
        session.commit()
        return book

    @staticmethod
    def save_chapter_to_db(book, chapter_title, content):
        chapter = Chapter(
            book_id=book.id, title=chapter_title, content=content, status=False
        )
        session.add(chapter)
        session.commit()
        return chapter

    @staticmethod
    def mark_chapter_as_processed(chapter_id, processed_content):
        chapter = session.query(Chapter).filter_by(id=chapter_id).first()
        if chapter:
            chapter.processed = True
            chapter.processed_content = processed_content
            session.commit()

    @staticmethod
    def get_unprocessed_chapters():
        return session.query(Chapter).filter_by(processed=False).all()
