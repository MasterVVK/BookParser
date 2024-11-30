from fetcher.web_page_fetcher import WebPageFetcher
from database.database_manager import DatabaseManager
from llm_processor.llm_processor import LLMProcessor
from bs4 import BeautifulSoup

class ChapterParser:
    """Класс для парсинга глав книги."""

    def __init__(self, max_chapters=2):
        self.max_chapters = max_chapters
        self.chapter_count = 0

    def parse_chapter(self, url, book):
        """Парсинг одной главы и сохранение в базу данных."""
        try:
            html_content = WebPageFetcher.fetch_webpage_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')

            # Извлечение заголовка и текста главы
            chapter_title = soup.find('h1').text if soup.find('h1') else 'Без названия'
            chapter_body_tag = soup.find('div', class_='entry-content')

            if chapter_body_tag:
                self.clean_chapter_body(chapter_body_tag)
                chapter_body = ''.join(str(tag) for tag in chapter_body_tag.find_all(['p', 'h2', 'h3', 'br']))
                chapter_body = chapter_body.replace('\n', '').strip()

                # Сохраняем главу в базу данных
                chapter = DatabaseManager.save_chapter_to_db(book, chapter_title, chapter_body)

                # Обрабатываем текст главы через LLM
                processed_content = LLMProcessor.process_text(chapter_body)

                # Обновляем статус и сохраняем обработанный текст
                DatabaseManager.mark_chapter_as_processed(chapter.id, processed_content)

                self.chapter_count += 1
            return soup

        except Exception as e:
            print(f'Ошибка при обработке {url}: {e}')
            return None

    @staticmethod
    def clean_chapter_body(chapter_body_tag):
        """Удаляет нежелательные элементы из текста главы."""
        for unwanted in chapter_body_tag.find_all(['a', 'script', 'style', 'iframe', 'ins']):
            unwanted.decompose()
