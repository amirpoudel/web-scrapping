import requests
from bs4 import BeautifulSoup
import os
import csv
from urllib.parse import urlparse

# List of domains to exclude from scraping
excluded_domains = ["github.com", "skills.github.com", "docs.github.com", "services.github.com", "socialimpact.github.com", "lab.github.com", "twitter.com", "help.twitter.com"]

# Function to save URLs to a local file
def save_urls(urls):
    with open('visited_urls.txt', 'a') as file:
        for url in urls:
            file.write(url + '\n')

# Function to load URLs from a local file
def load_urls():
    if not os.path.exists('visited_urls.txt'):
        return set()
    with open('visited_urls.txt', 'r') as file:
        return set(file.read().splitlines())

# Function to create a folder for domain and subdomain
def create_folder(url):
    domain = urlparse(url).netloc
    subdomain = '.'.join(domain.split('.')[:-2])
    if subdomain:
        folder_name = os.path.join('scraped_data', domain, subdomain)
    else:
        folder_name = os.path.join('scraped_data', domain)
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

# Function to scrape and save the page
def scrape_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        file_name = os.path.join(create_folder(url), 'index.html')
        with open(file_name, 'wb') as file:
            file.write(soup.prettify().encode('utf-8'))
        return file_name
    return None

# Function to get all links from a page
def get_links(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a', href=True)]
        return [link for link in links if link.startswith('http')]
    return []

# Function to scrape recursively
def scrape_recursively(url):
    visited_urls = load_urls()
    if url in visited_urls:
        print(f"{url} has already been visited")
        return
    print(f"Scraping {url}...")
    visited_urls.add(url)
    save_urls(visited_urls)
    file_path = scrape_page(url)
    if file_path:
        with open('scraped_urls.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([url, file_path])
        links = get_links(url)
        for link in links:
            domain = urlparse(link).netloc
            if domain not in excluded_domains:
                scrape_recursively(link)

# Main function
def main(start_url):
    if not os.path.exists('scraped_data'):
        os.makedirs('scraped_data')
    if not os.path.exists('scraped_urls.csv'):
        with open('scraped_urls.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['URL', 'File Path'])
    scrape_recursively(start_url)

# Test the scraper with a starting URL
start_url = 'https://attack.mitre.org/'
main(start_url)