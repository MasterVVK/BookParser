from parsers.book_parser import BookParser

if __name__ == '__main__':
    start_url = 'https://wuxiaworld.ru/imperator-syanvu/kontrataka-izgnannogo-uchenika-glava-1-uchenik-sekty/'
    book_title = 'Контратака изгнанного ученика'
    max_chapters = 1  # Указываем максимальное количество глав

    book_parser = BookParser(start_url, book_title, max_chapters=max_chapters)
    book_parser.parse_book()
