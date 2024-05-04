import requests
from bs4 import BeautifulSoup
import os
import csv
from urllib.parse import urlparse

class WebScraper:
    def __init__(self, folder_name):
        self.folder_name = folder_name

    def save_urls(self, urls):
        with open(os.path.join(self.folder_name, 'visited_urls.txt'), 'a') as file:
            for url in urls:
                file.write(url + '\n')

    def load_urls(self):
        file_path = os.path.join(self.folder_name, 'visited_urls.txt')
        if not os.path.exists(file_path):
            return set()
        with open(file_path, 'r') as file:
            return set(file.read().splitlines())

    def create_folder(self, url):
        domain = urlparse(url).netloc
        subdomain = '.'.join(domain.split('.')[:-2])
        if subdomain:
            folder_path = os.path.join(self.folder_name, 'scraped_data', domain, subdomain)
        else:
            folder_path = os.path.join(self.folder_name, 'scraped_data', domain)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def scrape_page(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            file_name = os.path.join(self.create_folder(url), 'index.html')
            with open(file_name, 'wb') as file:
                file.write(soup.prettify().encode('utf-8'))
            return file_name
        return None

    def get_links(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a', href=True)]
            return [link for link in links if link.startswith('http')]
        return []

    def scrape_recursively(self, url, excluded_domains):
        visited_urls = self.load_urls()
        if url in visited_urls:
            print(f"{url} has already been visited")
            return
        print(f"Scraping {url}...")
        visited_urls.add(url)
        self.save_urls(visited_urls)
        file_path = self.scrape_page(url)
        if file_path:
            with open(os.path.join(self.folder_name, 'scraped_urls.csv'), 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                #remove main folder name from file path
                file_path = os.path.relpath(file_path, self.folder_name)
                writer.writerow([url, file_path])
            links = self.get_links(url)
            for link in links:
                domain = urlparse(link).netloc
                if domain not in excluded_domains:
                    self.scrape_recursively(link, excluded_domains)

    def start_scraping(self, start_url, excluded_domains):
        if not os.path.exists(os.path.join(self.folder_name, 'scraped_data')):
            os.makedirs(os.path.join(self.folder_name, 'scraped_data'))
        if not os.path.exists(os.path.join(self.folder_name, 'scraped_urls.csv')):
            with open(os.path.join(self.folder_name, 'scraped_urls.csv'), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['URL', 'File Path'])
        self.scrape_recursively(start_url, excluded_domains)




