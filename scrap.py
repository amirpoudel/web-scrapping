#scrap.py
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_safe_filename(s):
    return "".join(x for x in s if (x.isalnum() or x in "._- "))

def scrape_page(url, max_depth, current_depth=0, seen_urls=set(), max_links_per_page=10):
    if current_depth > max_depth:
        return

    if url in seen_urls:
        return
    seen_urls.add(url)

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}")
            return
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')

    site_name = urlparse(url).netloc
    dir_name = f"{site_name}_data"
    os.makedirs(dir_name, exist_ok=True)

    page_filename = f"{current_depth}_{get_safe_filename(urlparse(url).path)}.txt"
    filepath = os.path.join(dir_name, page_filename)

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(soup.get_text())
        file.write(f"\n\nScraped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"Saved data to {filepath}")

    # Introduce a delay to avoid overwhelming the server
    time.sleep(1)

    # Limit the number of links per page
    for link in links[:max_links_per_page]:
        href = link.get('href')
        if href and (href.startswith('http') or href.startswith('/')):
            full_url = urljoin(url, href)

            if is_valid_url(full_url):
                scrape_page(full_url, max_depth, current_depth + 1, seen_urls, max_links_per_page)

# URL to scrape, maximum depth and maximum links per page
url = "https://unit42.paloaltonetworks.com/threat-brief-ivanti-cve-2023-46805-cve-2024-21887/"
max_depth = 2
max_links_per_page = 5

scrape_page(url, max_depth, max_links_per_page=max_links_per_page)