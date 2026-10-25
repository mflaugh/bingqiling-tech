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

Contact: 652844@gmail.com · X: https://x.com/BingqilingTech
The whole folder is static, so it can be hosted as-is on GitHub Pages, Netlify or Cloudflare Pages.

## Languages (i18n)

The portfolio is available in English, 简体中文, 日本語, 한국어, Русский, Español and Deutsch.
It is fully static: strings live in `assets/strings.js`, and `assets/i18n.js` applies them.

- On the first visit the language comes from the browser (`navigator.languages`). If none of the supported languages match, it falls back to English.
- The header dropdown switches language and remembers the choice in `localStorage`.
- `?lang=zh|ja|ko|ru|es|de|en` links can be shared, e.g. `https://mflaugh.github.io/bingqiling-tech/?lang=ja`.
- `<html lang>`, the title and the meta description are localized, and `hreflang` alternates are in the `<head>`.
- On the demo pages the demo labels and disclaimers are translated. The fictional businesses' own content (the coffee shop, the bot conversation, book data) stays in English on purpose.
- Brand, legal name and USD prices are not translated.

`python verify_demos.py` checks every page in every language: no missing keys, no console errors, the correct `<html lang>`, and that the switcher, persistence and `?lang` all work. Add `--base https://mflaugh.github.io/bingqiling-tech/` to test the live site.
