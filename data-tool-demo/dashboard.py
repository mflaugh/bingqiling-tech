"""Builds a self-contained HTML dashboard from data/books.db (Demo project / sample build).

    python dashboard.py      # writes dashboard.html (no external JS/CSS, works offline)
"""
import html
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "data" / "books.db"
OUT = HERE / "dashboard.html"
PALETTE = ["#2563eb", "#0ea5e9", "#14b8a6", "#22c55e", "#eab308", "#f97316", "#ef4444", "#a855f7"]


def q(con, sql):
    return con.execute(sql).fetchall()


def vbar(data, w=520, h=260, color="#2563eb", fmt=str):
    """Vertical bar chart as inline SVG. data: [(label, value)]"""
    pad_l, pad_b, pad_t = 40, 36, 20
    mx = max(v for _, v in data) or 1
    bw = (w - pad_l - 10) / len(data)
    out = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for i in range(5):
        y = pad_t + (h - pad_t - pad_b) * i / 4
        out.append(f'<line x1="{pad_l}" x2="{w-5}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
                   f'<text x="{pad_l-6}" y="{y+4:.1f}" class="ax" text-anchor="end">{fmt(round(mx*(4-i)/4))}</text>')
    for i, (lab, v) in enumerate(data):
        bh = (h - pad_t - pad_b) * v / mx
        x, y = pad_l + i * bw + bw * 0.15, h - pad_b - bh
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*0.7:.1f}" height="{bh:.1f}" rx="4" fill="{color}">'
                   f'<title>{html.escape(str(lab))}: {fmt(v)}</title></rect>'
                   f'<text x="{x+bw*0.35:.1f}" y="{h-pad_b+16}" class="ax" text-anchor="middle">{html.escape(str(lab))}</text>')
    out.append("</svg>")
    return "".join(out)


def hbar(data, w=520, fmt=lambda v: f"£{v:.2f}"):
    row, pad_l = 30, 165
    h = row * len(data) + 10
    mx = max(v for _, v in data) or 1
    out = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for i, (lab, v) in enumerate(data):
        y, bw = 5 + i * row, (w - pad_l - 60) * v / mx
        out.append(f'<text x="{pad_l-8}" y="{y+15}" class="ax" text-anchor="end">{html.escape(lab[:22])}</text>'
                   f'<rect x="{pad_l}" y="{y+3}" width="{bw:.1f}" height="{row-8}" rx="4" fill="{PALETTE[i % len(PALETTE)]}"/>'
                   f'<text x="{pad_l+bw+6:.1f}" y="{y+15}" class="ax">{fmt(v)}</text>')
    out.append("</svg>")
    return "".join(out)


def build():
    con = sqlite3.connect(DB)
    total, avg, mn, mx, instock, scraped = q(con, "select count(*), avg(price_gbp), min(price_gbp), max(price_gbp), "
                                                  "sum(in_stock), max(scraped_at) from books")[0]
    ncat = q(con, "select count(distinct category) from books")[0][0]
    avg_rating = q(con, "select avg(rating) from books")[0][0]
    by_rating = [(f"{r}★", n) for r, n in q(con, "select rating, count(*) from books group by rating order by rating")]
    bins = q(con, "select cast(price_gbp/10 as int)*10 b, count(*) from books group by b order by b")
    hist = [(f"£{b}–{b+10}", n) for b, n in bins]
    real = "category not in ('Default', 'Add a comment')"  # site placeholder categories, excluded from category charts
    top_cats = q(con, f"select category, avg(price_gbp) from books where {real} group by category having count(*)>=10 "
                      "order by avg(price_gbp) desc limit 8")
    low_cats = q(con, f"select category, avg(price_gbp) from books where {real} group by category having count(*)>=10 "
                      "order by avg(price_gbp) asc limit 8")
    cnt_cats = q(con, f"select category, count(*) from books where {real} group by category order by count(*) desc limit 8")
    price_by_rating = [(f"{r}★", round(p, 2)) for r, p in
                       q(con, "select rating, avg(price_gbp) from books group by rating order by rating")]
    rows = [dict(zip(["title", "price", "rating", "category", "url"], r)) for r in
            q(con, "select title, price_gbp, rating, category, url from books order by title")]
    con.close()

    kpi = lambda label, val: f'<div class="kpi"><span>{label}</span><strong>{val}</strong></div>'
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Book Market Dashboard — Demo project</title>
<style>
:root{{--bg:#f6f8fb;--card:#fff;--ink:#0f172a;--muted:#64748b}}*{{box-sizing:border-box}}
body{{margin:0;font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink)}}
.banner{{background:#0f172a;color:#cbd5e1;text-align:center;font-size:.82rem;padding:.4rem}}
header{{padding:1.6rem 4vw .6rem}}h1{{margin:0;font-size:1.7rem}}header p{{margin:.3rem 0 0;color:var(--muted)}}
main{{padding:1rem 4vw 3rem;display:grid;gap:1.2rem}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem}}
.kpi,.card{{background:var(--card);border-radius:14px;padding:1.1rem 1.3rem;box-shadow:0 1px 3px rgba(15,23,42,.08)}}
.kpi span{{color:var(--muted);font-size:.85rem}}.kpi strong{{display:block;font-size:1.6rem}}
.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:1.2rem}}
.card h2{{margin:0 0 .6rem;font-size:1.05rem}}.chart{{width:100%;height:auto}}
.chart .grid{{stroke:#e2e8f0}}.chart .ax{{font-size:13px;fill:#475569}}
.tools{{display:flex;gap:.6rem;flex-wrap:wrap;margin-bottom:.8rem}}
input,select{{font:inherit;padding:.5rem .7rem;border:1px solid #cbd5e1;border-radius:8px}}input{{flex:1;min-width:200px}}
table{{width:100%;border-collapse:collapse;font-size:.9rem}}th,td{{text-align:left;padding:.45rem .5rem;border-bottom:1px solid #eef2f7}}
th{{cursor:pointer;user-select:none;color:var(--muted);font-weight:600}}th:hover{{color:var(--ink)}}
.tablewrap{{max-height:420px;overflow:auto}}footer{{color:var(--muted);font-size:.85rem;text-align:center;padding-bottom:2rem}}
@media (max-width:600px){{.charts{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="banner">Demo project / sample build. Data scraped from books.toscrape.com, a public sandbox site made for scraping practice. Prices are fictional.</div>
<header><h1>Book Market Dashboard</h1><p>Scraped {total} listings across {ncat} categories · last run {scraped[:16].replace('T', ' ')} UTC</p></header>
<main>
<section class="kpis">{kpi("Books tracked", total)}{kpi("Average price", f"£{avg:.2f}")}{kpi("Price range", f"£{mn:.0f}–£{mx:.0f}")}
{kpi("Average rating", f"{avg_rating:.2f} ★")}{kpi("In stock", f"{instock/total:.0%}")}{kpi("Categories", ncat)}</section>
<section class="charts">
<div class="card"><h2>Price distribution</h2>{vbar(hist, color="#2563eb")}</div>
<div class="card"><h2>Books by star rating</h2>{vbar(by_rating, color="#14b8a6")}</div>
<div class="card"><h2>Most expensive categories (avg price, ≥10 books)</h2>{hbar(top_cats)}</div>
<div class="card"><h2>Cheapest categories (avg price, ≥10 books)</h2>{hbar(low_cats)}</div>
<div class="card"><h2>Largest categories (book count)</h2>{hbar(cnt_cats, fmt=str)}</div>
<div class="card"><h2>Average price by rating</h2>{vbar(price_by_rating, color="#a855f7", fmt=lambda v: f"£{v}")}</div>
</section>
<section class="card"><h2>Browse listings</h2>
<div class="tools"><input id="q" placeholder="Search title…"><select id="cat"><option value="">All categories</option></select>
<select id="rat"><option value="">Any rating</option><option>5</option><option>4</option><option>3</option><option>2</option><option>1</option></select></div>
<div class="tablewrap"><table><thead><tr><th data-k="title">Title</th><th data-k="category">Category</th><th data-k="price">Price</th><th data-k="rating">Rating</th></tr></thead>
<tbody id="tb"></tbody></table></div><p id="count" style="color:var(--muted);margin:.6rem 0 0"></p></section>
</main><footer>Sample build by Bingqiling Tech: Python scraper → SQLite/CSV → static HTML dashboard.</footer>
<script>
const ROWS={json.dumps(rows)};
const tb=document.getElementById('tb'),q=document.getElementById('q'),cat=document.getElementById('cat'),rat=document.getElementById('rat');
[...new Set(ROWS.map(r=>r.category))].sort().forEach(c=>cat.add(new Option(c,c)));
let key='title',dir=1;
function esc(s){{return s.replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]))}}
function render(){{const t=q.value.toLowerCase();
 const r=ROWS.filter(x=>(!t||x.title.toLowerCase().includes(t))&&(!cat.value||x.category===cat.value)&&(!rat.value||x.rating==rat.value))
  .sort((a,b)=>(a[key]>b[key]?1:a[key]<b[key]?-1:0)*dir);
 tb.innerHTML=r.slice(0,300).map(x=>`<tr><td><a href="${{x.url}}" target="_blank" rel="noopener">${{esc(x.title)}}</a></td><td>${{esc(x.category)}}</td><td>£${{x.price.toFixed(2)}}</td><td>${{'★'.repeat(x.rating)}}</td></tr>`).join('');
 document.getElementById('count').textContent=`${{r.length}} matching books`+(r.length>300?' (showing first 300)':'');}}
document.querySelectorAll('th').forEach(th=>th.onclick=()=>{{dir=key===th.dataset.k?-dir:1;key=th.dataset.k;render();}});
[q,cat,rat].forEach(e=>e.oninput=render);render();
</script></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size//1024} KB)")


if __name__ == "__main__":
    build()
