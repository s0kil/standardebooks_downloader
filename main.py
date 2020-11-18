import os
import sys
import requests
from time import time as timer
from urllib.parse import urljoin, urlparse
from multiprocessing.pool import ThreadPool

from autoscraper import AutoScraper
from expression.core import pipe
from expression.collections import Seq, seq

from autoscraper import AutoScraper

standard_ebooks_url = "https://standardebooks.org/ebooks"


# Navigation Scraper
navigation_scraper = AutoScraper()
scraped_pages_urls = navigation_scraper.build(
    standard_ebooks_url,
    ["/ebooks/?page=2", "/ebooks/?page=3"]
)
pages_urls = Seq(scraped_pages_urls).pipe(
    seq.map(lambda page: urljoin(standard_ebooks_url, page)),
)


# Page Scraper
page_scraper = AutoScraper()
books_urls = page_scraper.build(
    standard_ebooks_url,
    [
        "/ebooks/ford-madox-ford/some-do-not",
        "/ebooks/booth-tarkington/the-turmoil",
        "/ebooks/anatole-france/penguin-island/a-w-evans",
        "/ebooks/edgar-allan-poe/the-narrative-of-arthur-gordon-pym-of-nantucket"
    ],
    update=True
)
for page in pages_urls:
    print(page)
    urls = page_scraper.get_result_similar(page)
    books_urls = list(set(books_urls + urls))
books_urls = Seq(books_urls).pipe(
    seq.map(lambda book_path: urljoin("https://standardebooks.org", book_path))
)


# Book Scraper
book_scraper = AutoScraper()

azw3s_with_thumbnails = [
    "/ebooks/henry-fielding/the-history-of-tom-jones-a-foundling/downloads/henry-fielding_the-history-of-tom-jones-a-foundling.azw3",
    "/ebooks/henry-fielding/the-history-of-tom-jones-a-foundling/downloads/thumbnail_4e2aa05093a56fecc2e1f7e015e8aa2967f56208_EBOK_portrait.jpg",
]
books_assets = book_scraper.build(
    "https://standardebooks.org/ebooks/henry-fielding/the-history-of-tom-jones-a-foundling",
    azw3s_with_thumbnails,
    update=True
)
for book in books_urls:
    print(book)
    assets = book_scraper.get_result_similar(book)
    books_assets = list(set(books_assets + assets))
books_assets = Seq(books_assets).pipe(
    seq.map(lambda asset_path: urljoin(
        "https://standardebooks.org", asset_path))
)

# Download Book Assets
books_dir = os.path.join(
    os.path.dirname(
        os.path.realpath(sys.argv[0])
    ),
    "books"
)
os.makedirs(books_dir, exist_ok=True)


def fetch_url(uri):
    file_name = os.path.basename(urlparse(uri).path)
    file_path = os.path.join(books_dir, file_name)
    r = requests.get(uri, stream=True)
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in r:
                f.write(chunk)
    return file_name


start = timer()
results = ThreadPool(8).imap_unordered(fetch_url, books_assets)
for path in results:
    print(path)
print(f"Elapsed Time: {timer() - start}")
