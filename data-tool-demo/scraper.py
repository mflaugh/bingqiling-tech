"""Book catalogue scraper (Demo project / sample build).

Scrapes https://books.toscrape.com, a public sandbox site built for scraping practice,
and saves the results to SQLite and CSV.

    python scraper.py                 # all 50 pages (~1000 books)
    python scraper.py --pages 5       # first 5 pages only
"""
import argparse
import csv
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
HERE = Path(__file__).parent
DATA = HERE / "data"


def get(session, url, retries=3):
    for i in range(retries):
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            r.encoding = "utf-8"
            return r.text
        except requests.RequestException:
            if i == retries - 1:
                raise
            time.sleep(2 ** i)


def category_map(session):
    """Maps each book URL to its category by reading the category listing pages."""
    soup = BeautifulSoup(get(session, BASE), "html.parser")
    cats = {}
    for a in soup.select(".side_categories ul li ul li a"):
        name, url = a.get_text(strip=True), urljoin(BASE, a["href"])
        while url:
            page = BeautifulSoup(get(session, url), "html.parser")
            for art in page.select("article.product_pod h3 a"):
                cats[urljoin(url, art["href"]).split("catalogue/")[-1]] = name
            nxt = page.select_one("li.next a")
            url = urljoin(url, nxt["href"]) if nxt else None
            time.sleep(0.1)
    return cats


def scrape(pages, delay=0.3):
    session = requests.Session()
    session.headers["User-Agent"] = "PortfolioDemoScraper/1.0 (sample build)"
    print("Reading categories...")
    cats = category_map(session)
    books, now = [], datetime.now(timezone.utc).isoformat(timespec="seconds")
    for p in range(1, pages + 1):
        url = urljoin(BASE, f"catalogue/page-{p}.html")
        soup = BeautifulSoup(get(session, url), "html.parser")
        pods = soup.select("article.product_pod")
        if not pods:
            break
        for pod in pods:
            a = pod.select_one("h3 a")
            href = urljoin(url, a["href"])
            rating_cls = [c for c in pod.select_one("p.star-rating")["class"] if c != "star-rating"][0]
            books.append({
                "title": a["title"],
                "price_gbp": float(pod.select_one(".price_color").get_text().replace("£", "").strip()),
                "rating": RATINGS.get(rating_cls, 0),
                "in_stock": "In stock" in pod.select_one(".availability").get_text(),
                "category": cats.get(href.split("catalogue/")[-1], "Unknown"),
                "url": href,
                "scraped_at": now,
            })
        print(f"page {p}: {len(pods)} books (total {len(books)})")
        time.sleep(delay)
    return books


def save(books):
    DATA.mkdir(exist_ok=True)
    with (DATA / "books.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(books[0]))
        w.writeheader(); w.writerows(books)
    con = sqlite3.connect(DATA / "books.db")
    con.execute("DROP TABLE IF EXISTS books")
    con.execute("""CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, price_gbp REAL, rating INTEGER,
                   in_stock INTEGER, category TEXT, url TEXT UNIQUE, scraped_at TEXT)""")
    con.executemany("INSERT OR REPLACE INTO books (title,price_gbp,rating,in_stock,category,url,scraped_at) "
                    "VALUES (:title,:price_gbp,:rating,:in_stock,:category,:url,:scraped_at)", books)
    con.commit(); con.close()
    print(f"Saved {len(books)} books to {DATA/'books.csv'} and {DATA/'books.db'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=50)
    save(scrape(ap.parse_args().pages))
