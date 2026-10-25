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
]
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    for src, out, vp, full in JOBS:
        pg = b.new_page(viewport=vp, device_scale_factor=1 if full else 2 if vp["width"] < 500 else 1)
        pg.on("pageerror", lambda e, s=src: errors.append(f"{s}: {e}"))
        pg.on("console", lambda m, s=src: errors.append(f"{s}: {m.text}") if m.type == "error" else None)
        pg.goto((ROOT / src).as_uri()); pg.wait_for_load_state("networkidle")
        pg.screenshot(path=SHOTS / out, full_page=full); pg.close()
        print("saved", SHOTS / out)
    b.close()
print("JS errors:", errors or "none")
