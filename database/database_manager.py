from database.models import Book, Chapter, session

class DatabaseManager:
    """Класс для управления операциями с базой данных."""

    @staticmethod
    def save_book_to_db(book_title, start_url, total_chapters=0, excluded_texts=None):
        """
        Сохранить книгу в базу данных или обновить её, если она уже существует.
        :param book_title: Название книги
        :param start_url: URL для начала парсинга книги
        :param total_chapters: Общее количество глав (по умолчанию 0)
        :param excluded_texts: Список исключаемых текстов (по умолчанию None)
        :return: Объект книги
        """
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
            # Обновляем данные книги
            book.start_url = start_url
            book.total_chapters = total_chapters
            if excluded_texts is not None:
                book.excluded_texts = excluded_texts
        session.commit()
        return book

    @staticmethod
    def save_chapter_to_db(book, chapter_number, chapter_title, content):
        """
        Сохранить или обновить главу в базе данных.
        :param book: Объект книги
        :param chapter_number: Номер главы
        :param chapter_title: Название главы
        :param content: Содержимое главы
        :return: Объект главы
        """
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
                status=True
            )
            session.add(chapter)
        session.commit()
        return chapter

    @staticmethod
    def mark_chapter_as_processed(chapter_id, processed_content):
        """
        Обновить статус главы как обработанной и сохранить обработанный текст.
        :param chapter_id: ID главы
        :param processed_content: Обработанный текст
        """
        chapter = session.query(Chapter).filter_by(id=chapter_id).first()
        if chapter:
            chapter.processed = True
            chapter.processed_content = processed_content
            session.commit()

    @staticmethod
    def get_unprocessed_chapters(book_id=None, start_chapter=None, end_chapter=None, order_by="chapter_number"):
        """
        Получить необработанные главы с возможностью фильтрации и сортировки.
        :param book_id: ID книги для фильтрации (по умолчанию None — все книги).
        :param start_chapter: Начальный номер главы (включительно).
        :param end_chapter: Конечный номер главы (включительно).
        :param order_by: Поле для сортировки (по умолчанию 'chapter_number').
        :return: Список необработанных глав.
        """
        query = session.query(Chapter).filter_by(book_id=book_id,processed=False)
        print(query)
        if book_id is not None:
            query = query.filter(Chapter.book_id == book_id)
            print(query)
        if start_chapter is not None:
            query = query.filter(Chapter.chapter_number >= start_chapter)
        if end_chapter is not None:
            query = query.filter(Chapter.chapter_number <= end_chapter)
        if order_by:
            query = query.order_by(getattr(Chapter, order_by).asc())

        return query.all()

    @staticmethod
    def get_processed_chapters(book_id, start_chapter=None, end_chapter=None):
        query = session.query(Chapter).filter_by(book_id=book_id, processed=True)
        if start_chapter:
            query = query.filter(Chapter.chapter_number >= start_chapter)
        if end_chapter:
            query = query.filter(Chapter.chapter_number <= end_chapter)
        chapters = query.all()
        return [(chapter.title, chapter.processed_content) for chapter in chapters]
