"""End-to-end checks of the HTML demos in headless Chrome."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).parent.resolve()
ok = lambda c, m: print(("PASS " if c else "FAIL ") + m) or c
res = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1280, "height": 800}); pg.goto((ROOT/"website-demo/index.html").as_uri())
    res.append(ok(pg.locator("#bean-grid .card").count() == 6, "website: 6 product cards render"))
    pg.click("[data-filter=dark]"); res.append(ok(pg.locator("#bean-grid .card").count() == 2, "website: roast filter (dark=2)"))
    pg.click("#contact-form button[type=submit]")
    res.append(ok("Please fill" in pg.inner_text("#form-result"), "website: empty form shows validation error"))
    pg.fill("[name=name]", "Test"); pg.fill("[name=email]", "test@example.com"); pg.fill("[name=message]", "Hello there, demo")
    pg.click("#contact-form button[type=submit]"); res.append(ok("Thanks, Test" in pg.inner_text("#form-result"), "website: valid form shows success"))
    res.append(ok(pg.inner_text("#open-status") in ("Open now", "Closed now"), "website: open/closed status"))
    m = b.new_page(viewport={"width": 390, "height": 844}); m.goto((ROOT/"website-demo/index.html").as_uri())
    res.append(ok(not m.is_visible(".nav-links a[href='#beans']"), "website mobile: menu hidden"))
    m.click(".nav-toggle"); res.append(ok(m.is_visible(".nav-links a[href='#beans']"), "website mobile: hamburger opens menu"))
    res.append(ok(m.evaluate("document.documentElement.scrollWidth<=innerWidth"), "website mobile: no horizontal overflow"))
    d = b.new_page(); d.goto((ROOT/"data-tool-demo/dashboard.html").as_uri())
    res.append(ok(d.locator("svg.chart").count() == 6, "dashboard: 6 charts"))
    res.append(ok("1000 matching" in d.inner_text("#count"), "dashboard: table holds 1000 rows"))
    d.fill("#q", "light"); res.append(ok(d.locator("#tb tr").count() > 0 and "1000" not in d.inner_text("#count"), "dashboard: search filters"))
    i = b.new_page(); i.goto((ROOT/"index.html").as_uri()); i.evaluate("document.querySelectorAll('img').forEach(im=>im.loading='eager')"); i.wait_for_timeout(1500)
    res.append(ok(i.evaluate("[...document.images].every(im=>im.complete&&im.naturalWidth>0)"), "index: all screenshots load"))
    t = i.inner_text("body")
    res.append(ok(all(x in t for x in ["Landing page","from $300","from $800","from $500","from $30/month","from $200","Final quote after a free scoping call."]), "index: pricing section complete"))
    res.append(ok("Jiangsu Bingqiling Information Technology Co., Ltd." in i.inner_text("footer"), "index: legal name in footer"))
    res.append(ok(i.locator("a[href='mailto:652844@gmail.com']").count() == 1 and i.locator("a[href='https://x.com/3Dfpkj9m84AFnI9']").count() == 1, "index: email + X links"))
    res.append(ok(i.locator(".badge").count() == 3 and "demo / sample builds" in t, "index: demo labels kept"))
    res.append(ok("[Company Name]" not in i.content() and "[email]" not in i.content(), "index: no leftover placeholders"))
    for href in ["website-demo/index.html", "telegram-bot-demo/demo.html", "data-tool-demo/dashboard.html",
                 "telegram-bot-demo/README.md", "data-tool-demo/README.md"]:
        res.append(ok((ROOT/href).exists(), f"index: link target exists {href}"))
    b.close()
print(f"{sum(res)}/{len(res)} passed")
