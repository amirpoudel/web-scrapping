from web_scrap import WebScraper
from crawl import WebCrawler
from scrap import Scraper


exclude_domains=  ["github.com", "skills.github.com", "docs.github.com", "services.github.com", "socialimpact.github.com", "lab.github.com", "twitter.com", "help.twitter.com"]
url='https://www.ndss-symposium.org/ndss2011/accepted-papers/'
max_depth=2

folder_name='ndss-symposium-2011'


def main():

    # web_scrap = WebScraper(folder_name)
    # web_scrap.start_scraping(url,excluded_domains)

    # crawl = WebCrawler(folder_name)
    # crawl.crawl_data(url, max_depth)

    scrap = Scraper(url,exclude_domains,folder_name,max_depth)
    scrap.scrape_page()



if __name__ == "__main__":
    main()

