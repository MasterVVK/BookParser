from ebooklib import epub

class EPUBGenerator:
    """Класс для генерации EPUB файлов из обработанных глав."""

    @staticmethod
    def create_epub(title, chapters, filename='output.epub'):
        """
        Создает EPUB файл из списка глав.
        :param title: Название книги
        :param chapters: Список глав в формате [(chapter_title, chapter_content), ...]
        :param filename: Имя файла для сохранения
        """
        book = epub.EpubBook()

        # Настройка метаданных
        book.set_identifier('id100001')
        book.set_title(title)
        book.set_language('ru')

        # Добавление глав
        chapter_list = []
        for idx, (chapter_title, chapter_content) in enumerate(chapters):
            chapter = epub.EpubHtml(title=chapter_title, file_name=f'chap_{idx + 1}.xhtml', lang='ru')
            chapter.content = chapter_content
            book.add_item(chapter)
            chapter_list.append(chapter)

        # Определение содержания и порядка
        book.toc = tuple(chapter_list)
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Добавление стандартного стиля
        style = 'BODY { font-family: Times, serif; }'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)

        # Установка порядка
        book.spine = ['nav'] + chapter_list

        # Сохранение файла
        epub.write_epub(filename, book)
        print(f'EPUB файл "{filename}" успешно создан!')
