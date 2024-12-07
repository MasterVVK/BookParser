from database.models import Book, Chapter, session

class DatabaseManager:
    """Класс для управления операциями с базой данных."""

    @staticmethod
    def save_book_to_db(book_title, start_url, total_chapters=0, excluded_texts=None):
        """Сохранить книгу в базу данных или обновить её, если она уже существует."""
        book = session.query(Book).filter_by(title=book_title).first()
        if not book:
            book = Book(
                title=book_title,
                start_url=start_url,
                total_chapters=total_chapters,
                excluded_texts=excluded_texts or []
            )
            session.add(book)
        else:
            book.start_url = start_url
            book.total_chapters = total_chapters
            if excluded_texts is not None:
                book.excluded_texts = excluded_texts
        session.commit()
        return book

    @staticmethod
    def save_chapter_to_db(book, chapter_number, chapter_title, content, url):
        """Сохранить или обновить главу в базе данных."""
        chapter = session.query(Chapter).filter_by(book_id=book.id, url=url).first()
        if chapter:
            chapter.title = chapter_title
            chapter.content = content
        else:
            chapter = Chapter(
                book_id=book.id,
                chapter_number=chapter_number,
                title=chapter_title,
                content=content,
                url=url
            )
            session.add(chapter)
        session.commit()
        return chapter

    @staticmethod
    def get_chapter_by_url(url, book_id):
        """Получить главу по URL."""
        return session.query(Chapter).filter_by(book_id=book_id, url=url).first()

    @staticmethod
    def update_chapter_next_url(chapter_id, next_url):
        """Обновить URL следующей главы для текущей главы."""
        chapter = session.query(Chapter).filter_by(id=chapter_id).first()
        if chapter:
            chapter.next_url = next_url
            session.commit()

    @staticmethod
    def mark_chapter_as_processed(chapter_id, processed_content):
        """Обновить статус главы как обработанной и сохранить обработанный текст."""
        chapter = session.query(Chapter).filter_by(id=chapter_id).first()
        if chapter:
            chapter.processed = True
            chapter.processed_content = processed_content
            session.commit()

    @staticmethod
    def get_unprocessed_chapters(book_id):
        """Получает необработанные главы книги по ID книги."""
        try:
            query = session.query(Chapter).filter(
                Chapter.book_id == book_id,
                Chapter.processed == False
            ).order_by(Chapter.chapter_number)

            chapters = query.all()
            return chapters
        except Exception as e:
            print(f"Ошибка при выборке необработанных глав для книги ID {book_id}: {e}")
            return []

    @staticmethod
    def get_processed_chapters(book_id, start_chapter=None, end_chapter=None):
        query = session.query(Chapter).filter_by(book_id=book_id, processed=True)
        if start_chapter:
            query = query.filter(Chapter.chapter_number >= start_chapter)
        if end_chapter:
            query = query.filter(Chapter.chapter_number <= end_chapter)
        chapters = query.all()
        return [(chapter.title, chapter.processed_content) for chapter in chapters]

    @staticmethod
    def mark_chapter_as_blocked(chapter_id):
        """Отметить главу как заблокированную и сохранить исходный текст."""
        chapter = session.query(Chapter).filter_by(id=chapter_id).first()
        if chapter:
            chapter.blocked = True
            chapter.processed_content = chapter.content  # Сохраняем исходный текст
            session.commit()
