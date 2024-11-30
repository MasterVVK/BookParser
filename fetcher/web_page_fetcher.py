import requests

class WebPageFetcher:
    """Класс для получения содержимого веб-страницы с заголовком User-Agent."""

    @staticmethod
    def fetch_webpage_content(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Выбросить исключение при ошибке
        return response.text
