from web_scrap import WebScraper
from crawl import WebCrawler
from scrap import Scraper


exclude_domains=  ["www.linkedin.com","www.youtube.com","www.facebook.com","www.twitter.com","www.github.com", "www.skills.github.com", "www.docs.github.com", "www.services.github.com", "www.socialimpact.github.com", "www.lab.github.com", "www.twitter.com", "www.help.twitter.com"]
url='https://www.ndss-symposium.org/wp-content/uploads/2017/09/schlegel.pdf'
max_depth=1

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

