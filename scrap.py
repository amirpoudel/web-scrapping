import os
import requests
import csv
from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import PyPDF2
from typing import List, Dict, Tuple, Any, Union

def is_file_empty(file_path):
    return os.stat(file_path).st_size == 0


class Scraper:
    def __init__(self, base_url,exclude_domains:List[str] ,folderPath, max_depth=3):
        self.base_url = base_url
        self.exclude_domains = exclude_domains
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

    def extract_filename_from_url(self,url):
        # Extract the filename from the URL
        filename = url.split("/")[-1]
        if filename == "":
            filename = url.split("/")[-2]

        # Remove or replace special characters with safe character like '-'
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '-', filename)
        return filename


    def extract_text_from_pdf(pdf_url):
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                with open("temp.pdf", "wb") as f:
                    f.write(response.content)
                with open("temp.pdf", "rb") as f:
                    pdf_reader = PyPDF2.PdfFileReader(f)
                    text = ""
                    for page_number in range(pdf_reader.numPages):
                        page = pdf_reader.getPage(page_number)
                        text += page.extractText()
                # Remove temporary PDF file
                os.remove("temp.pdf")
                return text
            else:
                print(f"Failed to download PDF: {pdf_url}")
                return None
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

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

    def should_exclude_domain(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return any(exclude_domain in domain for exclude_domain in self.exclude_domains)

    def download_pdf(self,url):
        file_name = self.extract_filename_from_url(url)
        pdf_file_path = os.path.join(self.folderPath, "data", file_name + ".pdf")  # Construct file path manually
        # Ensure that the directory exists, create it if not
        os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)          
        try:
            # Download PDF file
            response = requests.get(url)
            if response.status_code == 200:
                with open(pdf_file_path, 'wb') as file:
                    file.write(response.content)
                with open(self.scraped_url_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([f"data/{file_name}.pdf", url])
                self.add_visited_url(url)
            else:
                print(f"Failed to download PDF: {url}")
        except Exception as e:
             print(f"Error downloading PDF: {e}")

  
    def save_data(self, url, soup):
        file_name = self.extract_filename_from_url(url)
        if file_name == "":
            file_name = "home"
        file_path = os.path.join(self.folderPath, "data", file_name + ".txt")  # Construct file path manually
        scraped_urls_file = os.path.join(self.folderPath, 'scraped_urls.csv')

        # Ensure that the directory exists, create it if not
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as file:
                file.write(soup.get_text())
                file.write(f"\n\nScraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        with open(self.scraped_url_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"data/{file_name}.txt", url])

        self.add_visited_url(url)
            

    """
    def save_data(self, url, soup):
        file_name = self.split_url(url)
        if file_name == "":
            file_name = "home"
        file_path = os.path.join(self.folderPath, "data", file_name + ".txt") # Construct file path manually
        scraped_urls_file = os.path.join(self.folderPath, 'scraped_urls.csv')
        visited_urls_file = os.path.join(self.folderPath, 'visited_urls.csv')

        # Ensure that the directory exists, create it if not
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Check if the content is a PDF
        if soup.find("meta", attrs={"name": "generator", "content": "Adobe Acrobat"}):
            # Handle PDF file
            pdf_url = url
            pdf_text = self.extract_text_from_pdf(pdf_url)
            if pdf_text:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(pdf_text)
                    file.write(f"\n\nScraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                with open(scraped_urls_file, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([f"data/{file_name}.txt", url])
                self.add_visited_url(url)
            else:
                print(f"Failed to extract text from PDF: {pdf_url}")

        else:
            # Handle HTML content
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(soup.get_text())
                file.write(f"\n\nScraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            with open(scraped_urls_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"data/{file_name}.txt", url])

            self.add_visited_url(url)
    """

    def extract_text_from_pdf(self, pdf_url):
        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                with open("temp.pdf", "wb") as f:
                    f.write(response.content)
                with open("temp.pdf", "rb") as f:
                    pdf_reader = PyPDF2.PdfFileReader(f)
                    text = ""
                    for page_number in range(pdf_reader.numPages):
                        page = pdf_reader.getPage(page_number)
                        text += page.extractText()
                return text
            else:
                print(f"Failed to download PDF: {pdf_url}")
                return None
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

        

    # explore links on the page also save the html data
    def scrape_page(self, url=None, max_depth=None, current_depth=0):
        print(f" depth : {current_depth}")
        if url is None:
            url = self.base_url

        # if self.base_url not in url:
        #     print(f"Skipping URL {url} as it does not belong to the base URL {self.base_url}")
        #     return

        if max_depth is None:
            max_depth = self.max_depth

        if current_depth >= max_depth:
            return


        if self.is_visited_url(url):
            print(f"URL {url} has already been visited. Skipping...")
            return 
           
        time.sleep(2)
        print(f"Scraping {url}...")
        if url.endswith(".pdf") or url.endswith(".pdf/"):
            print("URL FOUND PDF ! URL : ",url)
            print("Downloading PDF.....")
            self.download_pdf(url)
            return

        else:
            html_data = self.get_html_data(url)
            if html_data:
                soup = BeautifulSoup(html_data, 'html.parser')
                #self.save_data(url, soup)
                links = soup.find_all('a', href=True)
                self.add_visited_url(url)
                for link in links:
                    absolute_url = urljoin(url, link['href'])
                    if absolute_url.startswith("https://www.ndss-symposium.org/ndss2011") or absolute_url.startswith("https://www.ndss-symposium.org/wp-content/uploads"):
                       
                        self.scrape_page(absolute_url, max_depth, current_depth + 1)
                    # if not self.should_exclude_domain(absolute_url):
                    #     self.scrape_page(absolute_url, max_depth, current_depth + 1)
