"""Takes portfolio screenshots with headless Chrome (Playwright)."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.resolve()
SHOTS = ROOT / "screenshots"; SHOTS.mkdir(exist_ok=True)
JOBS = [
    ("website-demo/index.html", "website-desktop.png", {"width": 1366, "height": 860}, False),
    ("website-demo/index.html", "website-mobile.png", {"width": 390, "height": 844}, False),
    ("website-demo/index.html", "website-full.png", {"width": 1366, "height": 860}, True),
    ("telegram-bot-demo/demo.html", "telegram-bot.png", {"width": 460, "height": 900}, False),
    ("data-tool-demo/dashboard.html", "data-dashboard.png", {"width": 1366, "height": 900}, False),
    ("data-tool-demo/dashboard.html", "data-dashboard-full.png", {"width": 1366, "height": 900}, True),
    ("index.html", "portfolio-index.png", {"width": 1366, "height": 860}, True),
    ("index.html?lang=zh", "portfolio-index-zh.png", {"width": 1366, "height": 860}, True),
    ("index.html?lang=ja", "portfolio-index-ja.png", {"width": 1366, "height": 860}, True),
    ("data-tool-demo/dashboard.html?lang=zh", "data-dashboard-zh.png", {"width": 1366, "height": 900}, False),
    ("website-demo/index.html?lang=ja", "website-mobile-ja.png", {"width": 390, "height": 844}, False),
] + [("index.html?lang=" + l, f"portfolio-index-{l}-top.png", {"width": 1366, "height": 860}, False)
     for l in ["zh", "ja", "ko", "ru", "es", "de"]]
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for src, out, vp, full in JOBS:
        pg = b.new_page(viewport=vp, device_scale_factor=1 if full else 2 if vp["width"] < 500 else 1)
        pg.on("pageerror", lambda e, s=src: errors.append(f"{s}: {e}"))
        pg.on("console", lambda m, s=src: errors.append(f"{s}: {m.text}") if m.type == "error" else None)
        path, _, q = src.partition("?")
        pg.goto((ROOT / path).as_uri() + "?" + (q or "lang=en")); pg.wait_for_load_state("networkidle")
        pg.evaluate("document.querySelectorAll('img').forEach(im=>im.loading='eager')"); pg.wait_for_timeout(800)
        pg.screenshot(path=SHOTS / out, full_page=full); pg.close()
        print("saved", SHOTS / out)
    b.close()
print("JS errors:", errors or "none")
