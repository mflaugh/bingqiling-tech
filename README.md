# Bingqiling Tech (Jiangsu Bingqiling Information Technology Co., Ltd.): demo portfolio

All projects here are **demo projects / sample builds** made by us for fictional businesses. They are not client work.

| Path | What it is | How to run |
|---|---|---|
| `index.html` | Portfolio landing page | open in a browser |
| `website-demo/` | Static marketing site for a fictional coffee roaster (HTML/CSS/JS) | open `index.html` |
| `telegram-bot-demo/` | Telegram booking-intake bot (python-telegram-bot) | `python simulate.py`, `pytest -q`; `TELEGRAM_BOT_TOKEN=... python bot.py` |
| `data-tool-demo/` | books.toscrape.com scraper → SQLite/CSV → HTML dashboard | `python scraper.py && python dashboard.py` |
| `screenshots/` | PNG screenshots (headless Chrome) | `python take_screenshots.py` |
| `verify_demos.py` | Headless-browser end-to-end checks | `python verify_demos.py` |

Contact: 652844@gmail.com · X: https://x.com/3Dfpkj9m84AFnI9
The whole folder is static, so it can be hosted as-is on GitHub Pages, Netlify or Cloudflare Pages.
