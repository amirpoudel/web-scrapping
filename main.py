from web_scrap import WebScraper
from crawl import WebCrawler
from scrap import Scraper


excluded_domains=  ["github.com", "skills.github.com", "docs.github.com", "services.github.com", "socialimpact.github.com", "lab.github.com", "twitter.com", "help.twitter.com"]
url='https://www.usenix.org/conference/usenixsecurity24/summer-accepted-papers'
max_depth=2

folder_name='usenix_security_24'


def main():

    # web_scrap = WebScraper(folder_name)
    # web_scrap.start_scraping(url,excluded_domains)

    # crawl = WebCrawler(folder_name)
    # crawl.crawl_data(url, max_depth)

    scrap = Scraper(url,folder_name,3)
    scrap.scrape_page()



if __name__ == "__main__":
    main()

