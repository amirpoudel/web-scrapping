import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re

def sanitize_filename(filename):
    """Remove invalid characters from filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def fetch_and_save(url, depth, current_depth=1, visited=None):
    if visited is None:
        visited = set()

    try:
        # Avoid re-visiting the same URL
        if url in visited:
            return
        visited.add(url)

        # Send a GET request to the URL
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}: Status code {response.status_code}")
            return

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the title of the page to use as the filename
        title = soup.title.string if soup.title else 'Untitled'
        filename = sanitize_filename(title) + '.html'

        # Save the content in a file
        with open(os.path.join('data', filename), 'w', encoding='utf-8') as file:
            file.write(soup.prettify())

        print(f"Saved {url} as {filename}")

        # If the depth is reached, stop
        if current_depth == depth:
            return

        # Find all links on the page and recursively fetch them
        for link in soup.find_all('a', href=True)[:5]:  # Limit the number of links
            href = urljoin(url, link['href'])
            fetch_and_save(href, depth, current_depth + 1, visited)

    except Exception as e:
        print(f"An error occurred with {url}: {e}")

# Create 'data' directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Example usage
fetch_and_save("https://www.cisa.gov/news-events/alerts/2014/04/08/openssl-heartbleed-vulnerability-cve-2014-0160", depth=2)  # Change the depth as needed