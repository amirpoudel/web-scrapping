import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

class WebCrawler:
    def __init__(self, folder_name):
        self.folder_name = folder_name
        self.visited = set()
        self.data_folder_path = os.path.join(self.folder_name, 'data')

    def sanitize_filename(self, filename):
        """Remove invalid characters from filenames."""
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def fetch_and_save(self, url, depth, current_depth=1):
        try:
            # Avoid re-visiting the same URL
            if url in self.visited:
                return
            self.visited.add(url)

            # Send a GET request to the URL
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve {url}: Status code {response.status_code}")
                return

            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Get the title of the page to use as the filename
            title = soup.title.string if soup.title else 'Untitled'
            filename = self.sanitize_filename(title) + '.html'

            # Save the content in a file
            folder_path = os.path.join(self.data_folder_path, self.sanitize_filename(url))
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(soup.prettify())

            print(f"Saved {url} as {filename}")

            # If the depth is reached, stop
            if current_depth == depth:
                return

            # Find all links on the page and recursively fetch them
            for link in soup.find_all('a', href=True)[:5]:  # Limit the number of links
                href = urljoin(url, link['href'])
                self.fetch_and_save(href, depth, current_depth + 1)

        except Exception as e:
            print(f"An error occurred with {url}: {e}")

    def crawl_data(self, start_url, depth):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)
        if not os.path.exists(self.data_folder_path):
            os.makedirs(self.data_folder_path)
        self.fetch_and_save(start_url, depth)


