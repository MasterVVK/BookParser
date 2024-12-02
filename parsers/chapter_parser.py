import time
from fetcher.web_page_fetcher import WebPageFetcher
from database.database_manager import DatabaseManager
from llm_processor.llm_processor import LLMProcessor
from bs4 import BeautifulSoup

class ChapterParser:
    """Класс для парсинга глав книги."""

    def __init__(self, max_chapters=2, delay=2):
        self.max_chapters = max_chapters
        self.chapter_count = 0
        self.delay = delay  # Задержка между запросами

    def parse_chapter(self, url, book):
        """Парсинг одной главы и сохранение в базу данных."""
        try:
            if self.chapter_count >= self.max_chapters:
                print("Достигнуто максимальное количество глав.")
                return None

            html_content = WebPageFetcher.fetch_webpage_content(url)
            soup = BeautifulSoup(html_content, 'html.parser')

            # Извлечение заголовка и текста главы
            chapter_title = soup.find('h1').text if soup.find('h1') else 'Без названия'
            chapter_body_tag = soup.find('div', class_='entry-content')

            if chapter_body_tag:
                self.clean_chapter_body(chapter_body_tag, book.excluded_texts)
                chapter_body = ''.join(str(tag) for tag in chapter_body_tag.find_all(['p', 'h2', 'h3', 'br']))
                chapter_body = chapter_body.replace('\n', '').strip()

                if not chapter_body:
                    print(f"Текст главы отсутствует для {url}. Пропускаем.")
                    return None

                # Сохраняем главу в базу данных
                chapter = DatabaseManager.save_chapter_to_db(
                    book=book,
                    chapter_number=self.chapter_count + 1,
                    chapter_title=chapter_title,
                    content=chapter_body
                )

                # Обрабатываем текст главы через LLM
                #processed_content = LLMProcessor.process_text(chapter_body)

                # Обновляем статус и сохраняем обработанный текст
                #DatabaseManager.mark_chapter_as_processed(chapter.id, processed_content)

                self.chapter_count += 1
                print(f'Глава "{chapter_title}" успешно добавлена.')
            else:
                print(f'Текст главы не найден для {url}')

            # Найти URL следующей главы (кнопка с rel="Вперед")
            next_button = soup.find('a', rel='Вперед')
            next_url = next_button['href'] if next_button else None

            # Пауза перед запросом следующей главы
            print(f'Пауза {self.delay} секунд перед парсингом следующей главы...')
            time.sleep(self.delay)

            return next_url

        except Exception as e:
            print(f'Ошибка при обработке {url}: {e}')
            return None

    @staticmethod
    def clean_chapter_body(chapter_body_tag, excluded_texts):
        """Удаляет нежелательные элементы и тексты из тела главы."""
        for unwanted in chapter_body_tag.find_all(['a', 'script', 'style', 'iframe', 'ins']):
            unwanted.decompose()

        # Удаляем тексты из excluded_texts
        if excluded_texts:
            for unwanted_text in excluded_texts:
                for unwanted in chapter_body_tag.find_all(string=lambda text: unwanted_text in text):
                    unwanted.extract()

