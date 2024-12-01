from database.database_manager import DatabaseManager
from parsers.epub_generator import EPUBGenerator
from database.models import Book, session

def export_book_to_epub(book_id):
    """
    Экспортирует обработанные главы книги в формат EPUB.
    :param book_id: ID книги
    """
    # Получение информации о книге
    book = session.query(Book).filter_by(id=book_id).first()
    if not book:
        print(f'Книга с ID {book_id} не найдена.')
        return

    # Получение обработанных глав
    chapters = DatabaseManager.get_processed_chapters(book_id)
    if not chapters:
        print(f'Обработанные главы для книги "{book.title}" не найдены.')
        return

    # Лог для проверки
    print(f"Обнаружено {len(chapters)} обработанных глав для книги '{book.title}'.")

    # Формирование имени файла на основе названия книги
    safe_title = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in book.title).strip()
    output_file = f"{safe_title}.epub"

    # Создание EPUB
    EPUBGenerator.create_epub(book.title, chapters, filename=output_file)
    print(f'Книга "{book.title}" успешно экспортирована в файл "{output_file}".')
