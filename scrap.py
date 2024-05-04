import os
import requests
import csv
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re

def is_file_empty(file_path):
    return os.stat(file_path).st_size == 0


class Scraper:
    def __init__(self, base_url, folderPath, max_depth=3):
        self.base_url = base_url
        self.max_depth = max_depth
        self.visited_url_path = os.path.join(folderPath, 'visited_urls.csv')
        self.scraped_url_path = os.path.join(folderPath,'scraped_urls.csv')
        
        self.folderPath = folderPath
        self.visited_urls = set()
        # Ensure that the directory exists, create it if not
        os.makedirs(folderPath, exist_ok=True)

        #write row in scaped_urls_csv
        # Open the file in append mode ("a+")
        with open(self.scraped_url_path, 'a+', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row if the file is empty
            if is_file_empty(file_path=self.scraped_url_path):
                writer.writerow(["file", "source"])
    # extract name for file from url 
    def split_url(self, url):
        # Remove the base URL
        path = url.replace(self.base_url, "")

        # Remove query parameters and fragments from the URL
        path = path.split('?', 1)[0].split('#', 1)[0]

        # Sanitize the path to remove invalid characters for file names
        path = re.sub(r'[<>:"/\\|?*]', '-', path)

        # Remove leading and trailing dashes
        path = path.strip('-')

        # Remove leading slashes
        path = path.lstrip('/')

        return path


    def get_html_data(self, url):
        try:
            response = requests.get(url)
            if response.status_code==200:
                return response.text
            else:
                return None
        except requests.RequestException as e:
            print(f"Error fetching HTML data from {url}: {e}")
            return None

    # save html data on file - working on this 
    def add_visited_url(self, url):
        with open(self.visited_url_path, 'a', newline="", encoding='utf-8') as visited_file:
            if not self.is_visited_url(url):
                writer =  csv.writer(visited_file)
                writer.writerow([url])
                

    def is_visited_url(self, url):
        if not os.path.exists(self.visited_url_path):
            return False
        with open(self.visited_url_path, 'r', encoding='utf-8') as visited_file:
            return url in visited_file.read().splitlines()

    def save_data(self, url, soup):
        file_name = self.split_url(url)
        if file_name == "":
            file_name = "home"
        file_path = os.path.join(self.folderPath, "data", file_name + ".txt") # Construct file path manually
        scraped_urls_file = os.path.join(self.folderPath, 'scraped_urls.csv')
        visited_urls_file = os.path.join(self.folderPath, 'visited_urls.csv')
       
        # Ensure that the directory exists, create it if not
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(soup.get_text())
            file.write(f"\n\nScraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        with open(scraped_urls_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"data/{file_name}.txt", url])

        self.add_visited_url(url)

        

    # explore links on the page also save the html data
    def scrape_page(self, url=None, max_depth=None, current_depth=0):
        print(f" depth : {current_depth}")
        if url is None:
            url = self.base_url

        if self.base_url not in url:
            print(f"Skipping URL {url} as it does not belong to the base URL {self.base_url}")
            return

        if max_depth is None:
            max_depth = self.max_depth

        if current_depth > max_depth:
            return


        if self.is_visited_url(url):
            print(f"URL {url} has already been visited. Skipping...")
            return 
           
        time.sleep(2)
        html_data = self.get_html_data(url)
        if html_data:
            soup = BeautifulSoup(html_data, 'html.parser')
            self.save_data(url, soup)
            with open(self.visited_url_path, 'a', encoding='utf-8') as visited_file:
                visited_file.write(url + '\n')
            soup = BeautifulSoup(html_data, 'html.parser')
            links = soup.find_all('a', href=True)

            for link in links:
                absolute_url = urljoin(url, link['href'])
                if absolute_url.startswith(self.base_url):
                    self.scrape_page(absolute_url, max_depth, current_depth + 1)
