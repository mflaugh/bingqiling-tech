# Data tool demo: Book Market Scraper + Dashboard (Demo project)

**Demo project / sample build.** This is not client work. The data comes from [books.toscrape.com](https://books.toscrape.com),
a public sandbox site made for scraping practice. Its prices and ratings are fictional.

Pipeline: `scraper.py` → `data/books.db` (SQLite) + `data/books.csv` → `dashboard.py` → `dashboard.html`

- Scraper: requests + BeautifulSoup, with polite delays, retries and backoff, and a custom User-Agent. It collects title, price, rating, stock and category for all 1,000 books.
- Storage: CSV for spreadsheets, SQLite for queries.
- Dashboard: a single self-contained HTML file with KPIs, SVG charts (price distribution, ratings, category comparisons) and a searchable, filterable, sortable table. It has no external dependencies and works offline.

```bash
pip install -r requirements.txt
python scraper.py            # ~40 s for all 50 pages; --pages 5 for a quick run
python dashboard.py
open dashboard.html
```
For a client build, this could be scheduled daily (cron or GitHub Actions), add price-change alerts (email or Telegram),
or export to Google Sheets. Real-world scraping is only done where the site's terms and robots.txt allow it.
