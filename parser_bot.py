import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import urljoin, urlparse
import os

# Настроим логирование
logging.basicConfig(filename='emails_log.txt', 
                    format='%(asctime)s - %(message)s', 
                    level=logging.INFO)

# Регулярное выражение для поиска email
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

class EmailCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited_urls = set()
        self.emails_found = set()
    
    def crawl(self, url):
        """Основной метод для рекурсивного обхода страниц сайта"""
        if url in self.visited_urls:
            return
        
        print(f"Посещаем: {url}")
        self.visited_urls.add(url)
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверяем статус ответа
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем и сохраняем все email на этой странице
            self.find_emails(soup, url)
            
            # Находим все ссылки на странице и продолжаем обход
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Проверяем, что ссылка ведет на тот же домен
                if self.is_same_domain(full_url):
                    self.crawl(full_url)
        
        except requests.RequestException as e:
            print(f"Ошибка при обращении к {url}: {e}")
    
    def find_emails(self, soup, page_url):
        """Ищет email в тексте страницы"""
        text = soup.get_text()
        emails = re.findall(EMAIL_REGEX, text)
        for email in emails:
            if email not in self.emails_found:
                self.emails_found.add(email)
                logging.info(f"Email: {email}, URL: {page_url}")
                print(f"Найден email: {email} на странице {page_url}")
    
    def is_same_domain(self, url):
        """Проверяет, что URL принадлежит тому же домену, что и начальный сайт"""
        base_domain = urlparse(self.base_url).netloc
        target_domain = urlparse(url).netloc
        return base_domain == target_domain

if __name__ == "__main__":
    base_url = 'https://example.com'  # Введите начальный URL сайта
    crawler = EmailCrawler(base_url)
    crawler.crawl(base_url)

    print(f"Обход завершен. Найдено {len(crawler.emails_found)} email(ов).")
