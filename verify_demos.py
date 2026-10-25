"""End-to-end checks of the HTML demos and i18n in headless Chrome.

    python verify_demos.py                      # local files
    python verify_demos.py --base https://mflaugh.github.io/bingqiling-tech/   # live site
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.resolve()
BASE = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else None
LANGS = {"en": "en", "zh": "zh-Hans", "ja": "ja", "ko": "ko", "ru": "ru", "es": "es", "de": "de"}
PAGES = ["index.html", "website-demo/index.html", "telegram-bot-demo/demo.html", "data-tool-demo/dashboard.html"]
CHECK_KEY = {"index.html": ("h1", "hero.title"), "website-demo/index.html": (".demo-banner", "site.banner"),
             "telegram-bot-demo/demo.html": (".note", "bot.note"), "data-tool-demo/dashboard.html": ("h1", "dash.title")}


def url(page, query=""):
    if BASE:
        return BASE.rstrip("/") + "/" + ("" if page == "index.html" else page) + query
    return (ROOT / page).as_uri() + query


res = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m); res.append(bool(c)); return c


def collect(pg, bucket):
    pg.on("pageerror", lambda e: bucket.append(f"pageerror: {e}"))
    pg.on("console", lambda m: bucket.append(f"console.{m.type}: {m.text}") if m.type in ("error", "warning") else None)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])

    # --- static: same key set in every language ---
    pg = b.new_page(); pg.goto(url("index.html", "?lang=en"))
    S = pg.evaluate("window.I18N_STRINGS")
    en_keys = set(S["en"])
    for l in LANGS:
        ok(set(S.get(l, {})) == en_keys, f"strings: '{l}' has exactly the {len(en_keys)} English keys")
    pg.close()

    # --- every page x every language ---
    for page in PAGES:
        sel, key = CHECK_KEY[page]
        for l, html_lang in LANGS.items():
            ctx = b.new_context(locale="en-US"); pg = ctx.new_page(); errs = []; collect(pg, errs)
            pg.goto(url(page, f"?lang={l}")); pg.wait_for_load_state("networkidle")
            missing = pg.evaluate("window.__i18nMissing")
            used = pg.evaluate("[...document.querySelectorAll('[data-i18n]')].map(e=>e.dataset.i18n).concat([...document.querySelectorAll('[data-i18n-attr]')].flatMap(e=>e.dataset.i18nAttr.split(';').map(x=>x.split(':')[1])))")
            undefined_keys = [k for k in used if k not in S[l]]
            expect = pg.evaluate(f"(()=>{{const d=document.createElement('div');d.innerHTML=window.I18N_STRINGS['{l}']['{key}'];return d.textContent}})()")
            shown = pg.inner_text(sel).strip()
            good = (pg.evaluate("document.documentElement.lang") == html_lang and not missing and not undefined_keys
                    and not errs and shown == expect.strip() and pg.locator("select.lang-switch").input_value() == l)
            ok(good, f"{page} [{l}] lang={html_lang}, {len(used)} keys, translated, no missing/console errors"
               + ("" if good else f"  missing={missing} undef={undefined_keys} errs={errs} shown={shown[:50]!r}"))
            ctx.close()

    # --- auto-detect, fallback, switcher persistence, shareable URL ---
    for loc, want in [("ja-JP", "ja"), ("zh-CN", "zh"), ("ko-KR", "ko"), ("ru-RU", "ru"), ("de-DE", "de"), ("es-MX", "es"), ("fr-FR", "en")]:
        ctx = b.new_context(locale=loc); pg = ctx.new_page(); pg.goto(url("index.html"))
        ok(pg.evaluate("I18N.lang") == want, f"auto-detect: browser {loc} -> {want}"); ctx.close()
    ctx = b.new_context(locale="en-US"); pg = ctx.new_page(); pg.goto(url("index.html"))
    pg.select_option("select.lang-switch", "ru")
    ok(pg.evaluate("localStorage.getItem('bq_lang')") == "ru" and "lang=ru" in pg.url, "switcher: saves choice + updates ?lang= in URL")
    ok(pg.inner_text("#pricing h2") == S["ru"]["pricing.title"], "switcher: page re-translates without reload")
    pg.goto(url("index.html")); ok(pg.evaluate("I18N.lang") == "ru", "switcher: choice remembered on next visit")
    ok("lang=ru" in (pg.get_attribute("a[data-i18n='d1.open']", "href") or ""), "switcher: demo links carry ?lang")
    pg.goto(url("data-tool-demo/dashboard.html")); ok(pg.evaluate("I18N.lang") == "ru", "switcher: choice applies on demo pages")
    pg.goto(url("index.html", "?lang=ja")); ok(pg.evaluate("I18N.lang") == "ja", "?lang= overrides saved choice")
    ctx.close()

    # --- head: hreflang + meta description ---
    ctx = b.new_context(); pg = ctx.new_page(); pg.goto(url("index.html", "?lang=de"))
    hl = pg.evaluate("[...document.querySelectorAll('link[rel=alternate]')].map(l=>l.hreflang)")
    ok(sorted(hl) == sorted(list(LANGS.values()) + ["x-default"]), f"head: hreflang alternates {hl}")
    ok(pg.get_attribute("meta[name=description]", "content") == S["de"]["meta.desc"] and pg.title() == S["de"]["meta.title"], "head: localized title + meta description (de)")
    ctx.close()

    # --- functional demo checks (English) ---
    ctx = b.new_context(locale="en-US")
    pg = ctx.new_page(); pg.set_viewport_size({"width": 1280, "height": 800}); pg.goto(url("website-demo/index.html", "?lang=en"))
    ok(pg.locator("#bean-grid .card").count() == 6, "website: 6 product cards render")
    pg.click("[data-filter=dark]"); ok(pg.locator("#bean-grid .card").count() == 2, "website: roast filter (dark=2)")
    pg.click("#contact-form button[type=submit]"); ok("Please fill" in pg.inner_text("#form-result"), "website: empty form shows validation error")
    pg.fill("[name=name]", "Test"); pg.fill("[name=email]", "test@example.com"); pg.fill("[name=message]", "Hello there, demo")
    pg.click("#contact-form button[type=submit]"); ok("Thanks, Test" in pg.inner_text("#form-result"), "website: valid form shows success")
    ok(pg.inner_text("#open-status") in ("Open now", "Closed now"), "website: open/closed status")
    m = ctx.new_page(); m.set_viewport_size({"width": 390, "height": 844}); m.goto(url("website-demo/index.html", "?lang=en"))
    ok(not m.is_visible(".nav-links a[href='#beans']"), "website mobile: menu hidden")
    m.click(".nav-toggle"); ok(m.is_visible(".nav-links a[href='#beans']"), "website mobile: hamburger opens menu")
    for l in ["en", "ru", "de"]:
        for page in ["website-demo/index.html", "index.html"]:
            m.goto(url(page, f"?lang={l}")); ok(m.evaluate("document.documentElement.scrollWidth<=innerWidth"), f"mobile 390px: no horizontal overflow {page} [{l}]")
    d = ctx.new_page(); d.goto(url("data-tool-demo/dashboard.html", "?lang=en"))
    ok(d.locator("svg.chart").count() == 6, "dashboard: 6 charts")
    ok("1000 matching" in d.inner_text("#count"), "dashboard: table holds 1000 rows")
    d.fill("#q", "light"); ok(d.locator("#tb tr").count() > 0 and "1000" not in d.inner_text("#count"), "dashboard: search filters")
    d.goto(url("data-tool-demo/dashboard.html", "?lang=zh")); ok(d.inner_text("#count").startswith("共 1000"), "dashboard: count text translated (zh)")
    i = ctx.new_page(); i.goto(url("index.html", "?lang=en"))
    i.evaluate("document.querySelectorAll('img').forEach(im=>im.loading='eager')"); i.wait_for_timeout(1500)
    ok(i.evaluate("[...document.images].every(im=>im.complete&&im.naturalWidth>0)"), "index: all screenshots load")
    t = i.inner_text("body")
    ok(all(x in t for x in ["Landing page", "from $300", "from $800", "from $500", "from $30/month", "from $200", "Final quote after a free scoping call."]), "index: pricing section complete (en)")
    ok("Jiangsu Bingqiling Information Technology Co., Ltd." in i.inner_text("footer"), "index: legal name in footer")
    ok(i.locator("a[href='mailto:652844@gmail.com']").count() == 1 and i.locator("a[href='https://x.com/BingqilingTech']").count() == 1, "index: email + X links")
    ok(i.locator(".badge").count() == 3 and "demo / sample builds" in t, "index: demo labels kept")
    for l in LANGS:
        i.goto(url("index.html", f"?lang={l}"))
        ft, tt = i.inner_text("footer"), i.inner_text("body")
        ok("Jiangsu Bingqiling Information Technology Co., Ltd." in ft and "Bingqiling Tech" in tt and "$800" in tt and "$30" in tt
           and i.locator(".badge").count() == 3 and S[l]["pricing.note"] in tt,
           f"index [{l}]: brand/legal name in English, USD prices, 3 demo badges, pricing note")
    for d_ in ["website-demo", "telegram-bot-demo", "data-tool-demo"]:
        ok((ROOT / d_ / "README.md").exists(), f"index: source folder exists {d_}")
    b.close()
print(f"{sum(res)}/{len(res)} passed")
sys.exit(0 if all(res) else 1)
