#!/usr/bin/env python3
"""Static site generator for the Shreya Agro Foods website.

Run from anywhere:   python3 tools/build.py

Reads the product / category / job data below plus tools/src/{style.css,main.js} and writes the
finished static site (plain HTML + CSS + JS) into the repository root. The output is what gets
deployed — hosting needs no Python, PHP or database.

Edit content here (products, jobs, company details), re-run, commit. See README.md.
"""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "src")
IMG_DIR = os.path.join(ROOT, "assets", "images")

# --------------------------------------------------------------------------------------
# Company details
# --------------------------------------------------------------------------------------
DOMAIN = "https://www.shreyaagrofoods.com"
COMPANY = "Shreya Agro Foods Ltd."
BRAND = "Shreya Agro Foods"
TAGLINE = "Authentic Taste. Trusted Quality."
PHONE_DISPLAY = "+91 70586 74452"
PHONE_TEL = "+917058674452"
WHATSAPP = "917058674452"
EMAIL = "info@shreyaagrofoods.com"
ADDRESS = "411-412, Mastermind Rd, Royal Palms, Aarey Milk Colony, Goregaon East, Mumbai, Maharashtra 400065"
SOCIALS = [
    ("Facebook", "https://www.facebook.com/ShreyaAgroFoods/", "facebook"),
    ("Instagram", "https://www.instagram.com/shreyaagrofoodsofficiall_/", "instagram"),
    ("LinkedIn", "https://www.linkedin.com/company/shreyaagrfoodlimited/", "linkedin"),
]
LASTMOD = date.today().isoformat()
YEAR = date.today().year
MAP_SRC = "https://www.google.com/maps?q=Royal+Palms,+Aarey+Milk+Colony,+Goregaon+East,+Mumbai,+Maharashtra+400065&output=embed"

# --------------------------------------------------------------------------------------
# Catalogue data
# --------------------------------------------------------------------------------------
CATEGORIES = [
    dict(slug="masalas", name="Masalas", icon="leaf", img="spices-still-life", blend=False,
         desc="Authentic spices for richer flavours.", bg="#fdf6e6,#fbe6c6", ink="#1c5b3f", badge="#e3efe6"),
    dict(slug="pickles", name="Pickles", icon="jar", img="mango-pickle", blend=False,
         desc="Traditional taste, made with care.", bg="#f0f6e6,#dcebc9", ink="#2f7a4d", badge="#e0efd3"),
    dict(slug="sweets", name="Sweets", icon="cupcake", img="gulab-jamun-rasgulla", blend=True,
         desc="Sweet moments, made special.", bg="#fdeff0,#f9d8de", ink="#c0394f", badge="#fbdfe3"),
    dict(slug="soan-papdi", name="Soan Papdi", icon="package", img="soan-papdi-collection", blend=True,
         desc="Light, flaky and delicious.", bg="#fdf6e0,#f8e8b8", ink="#a9780f", badge="#faeec6"),
    dict(slug="jams", name="Jams", icon="jar", img="mix-fruit-jam", blend=True,
         desc="Pure fruit goodness in every bite.", bg="#fdeeed,#f8d2d2", ink="#b6313c", badge="#fbdcdc"),
    dict(slug="besan", name="Besan & Grains", icon="wheat", img="besan-chakki-atta", blend=True,
         desc="Pure, nutritious and versatile.", bg="#fcf4e2,#f2e2b8", ink="#a9780f", badge="#f7e9c4"),
    dict(slug="jaggery", name="Jaggery", icon="cube", img="jaggery-cubes-powder", blend=False,
         desc="Natural sweetness, with goodness.", bg="#ebf4e7,#d5e8cc", ink="#2d7a4f", badge="#dcecd3"),
    dict(slug="rusk", name="Rusk & Biscuits", icon="bread", img="rusk-toast-display", blend=False,
         desc="Crispy, crunchy, perfect with tea.", bg="#ecf4fb,#d2e5f6", ink="#2c6aa0", badge="#d9e9f7"),
]
CAT = {c["slug"]: c for c in CATEGORIES}

PRODUCTS = [
    dict(slug="basmati-rice", name="Premium Basmati Rice", cat="besan", type="Rice", packs="1kg, 5kg, 25kg",
         short="Extra-long grain basmati rice, naturally aged for 12 months to enhance its aroma, texture, and flavour.",
         images=[("basmati-rice", "Premium Basmati Rice pack with cooked rice"), ("rice-sack", "Premium Basmati Rice in a jute sack")]),
    dict(slug="besan-flour", name="Besan Chakki Ka Atta", cat="besan", type="Flour", packs="500g, 1kg, 30kg",
         short="Made from 100% pure Bengal gram (chana dal) finely milled for a smooth, lump-free texture.",
         images=[("besan-chakki-atta", "Besan Chakki Ka Atta pack")]),
    dict(slug="wheat-flour-atta", name="Wheat Flour (Chakki Atta)", cat="besan", type="Flour", packs="",
         short="100% whole wheat stone ground goodness. Rich in fiber and natural nutrition.",
         images=[("wheat-flour-atta", "Wheat Flour Chakki Atta packs with fresh rotis"), ("wheat-flour-kitchen", "Wheat Flour Chakki Atta in a kitchen setting")]),
    dict(slug="chicken-masala", name="Chicken & Meat Masalas", cat="masalas", type="Cooking Masala", packs="50g, 100g, 250g, 500g, 1kg, 5kg",
         short="Spicy and robust signature blends for classic Indian cooking.",
         images=[("chicken-meat-masalas", "Chicken Masala, Fish Curry Masala and Meat Masala range")]),
    dict(slug="spice-powders", name="Spice Powders", cat="masalas", type="Spice Powder", packs="50g, 100g, 250g, 500g, 1kg, 5kg",
         short="Coriander, red chilli, turmeric and garam masala powders with bright colour and pure aroma.",
         images=[("spice-powder-collection", "Coriander, chilli, turmeric and garam masala powder boxes"), ("spice-powders-poster", "Spice powders range with pack sizes"), ("spices-still-life", "Whole and ground spices")]),
    dict(slug="mango-pickle", name="Mango & Mix Pickle", cat="pickles", type="Pickle", packs="100g, 200g, 250g, 500g, 1kg, 5kg",
         short="Authentic taste bringing the true essence of Indian kitchens to your plate with time-honored recipes.",
         images=[("mango-pickle", "Mango pickle and mix pickle jars with fresh mangoes"), ("mango-mix-pickle-display", "Mango and mix pickle display")]),
    dict(slug="farm-fresh-pickles", name="Farm-Fresh Pickles", cat="pickles", type="Pickle", packs="100g, 200g, 250g, 500g, 1kg, 5kg",
         short="Authentic pickles packed with flavor and traditional spices.",
         images=[("farm-fresh-pickles", "Farm-fresh pickle jars in front of the Shreya facility"), ("pickles-fresh-ingredients", "Pickles with fresh ingredients")]),
    dict(slug="mint-chutney", name="Mint Chutney", cat="pickles", type="Chutney", packs="",
         short="A fresh, tangy mint chutney that pairs with snacks, meals and street-food favourites.",
         images=[("mint-chutney", "Mint chutney jar with fresh mint")]),
    dict(slug="gulab-jamun-rasgulla", name="Gulab Jamun & Rasgulla", cat="sweets", type="Indian Sweets", packs="500g, 1kg",
         short="Timeless taste of traditional Indian desserts, soft and syrup-soaked.",
         images=[("gulab-jamun-rasgulla", "Gulab Jamun and Rasgulla tins")]),
    dict(slug="soan-papdi-assorted", name="Assorted Soan Papdi", cat="soan-papdi", type="Soan Papdi", packs="180g, 200g",
         short="Crisp and flaky traditional sweet in assorted flavors.",
         images=[("soan-papdi-collection", "Assorted flavours of Soan Papdi"), ("soan-papdi-box", "Soan Papdi box with pieces")]),
    dict(slug="hardball-candy", name="Hardball Candy", cat="sweets", type="Candy", packs="Available in jars",
         short="A burst of vibrant, fruity flavors in delightful long-lasting hard candies.",
         images=[("hardball-candy", "Hardball candy jars and assorted candies")]),
    dict(slug="chikki", name="Chikki", cat="sweets", type="Chikki", packs="",
         short="Crunchy, nutty chikki made for everyday snacking and festive gifting.",
         images=[("chikki", "Shreya Chikki with nuts and jaggery")]),
    dict(slug="jaggery", name="Jaggery Cubes & Powder", cat="jaggery", type="Jaggery", packs="500g",
         short="Natural sweetener made from pure sun-ripened sugarcane juice.",
         images=[("jaggery-cubes-powder", "Jaggery cubes and jaggery powder jars"), ("jaggery-jars", "Jaggery cubes and powder in jars")]),
    dict(slug="mix-fruit-jam", name="Mix Fruit Jam", cat="jams", type="Jam", packs="250g, 500g, 1kg",
         short="Made with the finest fruits, our Mix Fruit Jam brings the perfect blend of taste, richness and natural goodness.",
         images=[("mix-fruit-jam", "Mix Fruit Jam jars"), ("jam-jar-closeup", "Mix Fruit Jam jar close-up")]),
    dict(slug="tomato-ketchup", name="Tomato Ketchup", cat="jams", type="Sauce", packs="500g, 1kg",
         short="Rich, tangy tomato ketchup made from quality tomatoes.",
         images=[("tomato-ketchup", "Tomato Ketchup bottle with fresh tomatoes")]),
    dict(slug="ginger-garlic-paste", name="Ginger & Garlic Paste", cat="jams", type="Paste", packs="500g, 1kg, 5kg",
         short="Balanced blend of fresh ginger and garlic processed to a fine, smooth texture.",
         images=[("ginger-garlic-paste", "Ginger and garlic paste jars with fresh ginger and garlic")]),
    dict(slug="rusk-toast", name="Rusk Toast (Elaichi & Milty Flavour)", cat="rusk", type="Rusk", packs="",
         short="Crunchy and tasty Rusk Toast perfect for your tea-time. Available in Elaichi and Milty flavors.",
         images=[("rusk-toast-tea-time", "Elaichi and Milty rusk toast with tea"), ("rusk-toast-display", "Rusk toast packs and slices")]),
    dict(slug="biscuits", name="Biscuits", cat="rusk", type="Biscuits", packs="",
         short="Crisp, tasty biscuits and cookies for tea-time and everyday snacking.",
         images=[("biscuits", "Assorted biscuits and cookies with milk")]),
]
PROD = {p["slug"]: p for p in PRODUCTS}
POPULAR = ["basmati-rice", "mix-fruit-jam", "farm-fresh-pickles", "chicken-masala"]

JOBS = [
    dict(title="Area Sales Manager (ASM)", location="Mumbai / Pune", type="Full Time",
         summary="Grow our distributor and retail network across your assigned territory.",
         details=["Develop and manage distributors, wholesalers and retail relationships in your territory.",
                  "Achieve monthly and quarterly sales targets and drive secondary sales.",
                  "Track market trends, competitor activity and share feedback with the leadership team."]),
    dict(title="Marketing Executive", location="Mumbai HQ", type="Full Time",
         summary="Help build the Shreya brand through campaigns, content and trade communication.",
         details=["Plan and execute brand, digital and trade marketing activities.",
                  "Create product, packaging and promotional content with the design team.",
                  "Coordinate with sales on launches, schemes and market promotions."]),
    dict(title="Senior Accounts Executive", location="Mumbai HQ", type="Full Time",
         summary="Keep our books accurate, compliant and on time.",
         details=["Handle day-to-day accounting, invoicing, reconciliations and GST filings.",
                  "Support month-end closing, audits and MIS reporting.",
                  "Coordinate with vendors, distributors and banks on payments and receivables."]),
]

# --------------------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------------------
e = html.escape


def q(s):
    """HTML attribute-safe string."""
    return html.escape(s, quote=True)


ICON_PATHS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    "bot": '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.6-3.3 8.3-8 9-4.7-.7-8-4.4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "truck": '<path d="M1 6h12v10H1z"/><path d="M13 9h4l4 4v3h-8"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="M8.5 14.5L7 22l5-3 5 3-1.5-7.5"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "headset": '<path d="M3 14v-2a9 9 0 0 1 18 0v2"/><path d="M21 15a2 2 0 0 1-2 2h-1v-5h1a2 2 0 0 1 2 2zM3 15a2 2 0 0 0 2 2h1v-5H5a2 2 0 0 0-2 2z"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.6 5-6.7 2.6-.9 5-.4 8-2"/>',
    "flask": '<path d="M10 2v7.5L4 20a1.5 1.5 0 0 0 1.3 2h13.4A1.5 1.5 0 0 0 20 20l-6-10.5V2M8.5 2h7M7 16h10"/>',
    "factory": '<path d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"/>',
    "bulb": '<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 .4-1.8 1-2.3A7 7 0 0 0 12 2z"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8M15 7h6v6"/>',
    "sprout": '<path d="M7 20h10M12 20v-9"/><path d="M12 11C12 7 9 5 5 5c0 4 2 6 7 6zM12 13c0-3 2-5 6-5 0 3-2 5-6 5z"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/><circle cx="12" cy="12" r="3"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "download": '<path d="M12 3v12M7 10l5 5 5-5M4 21h16"/>',
    "package": '<path d="M21 8l-9-5-9 5v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/>',
    "jar": '<path d="M8 3h8v3H8z"/><path d="M6 6h12v2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2z"/><path d="M8 13h8"/>',
    "cupcake": '<path d="M5 12h14l-1.5 8h-11z"/><path d="M6.5 12a5.5 5.5 0 0 1 11 0M12 4v2.5"/>',
    "wheat": '<path d="M12 22V9"/><path d="M12 9c0-3 2-5 4-5 0 3-1 5-4 5zM12 9c0-3-2-5-4-5 0 3 1 5 4 5zM12 15c0-3 2-5 4-5 0 3-1 5-4 5zM12 15c0-3-2-5-4-5 0 3 1 5 4 5z"/>',
    "cube": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12L4 7.5M12 12v9"/>',
    "bread": '<path d="M5 10a4 4 0 0 1 2-7h10a4 4 0 0 1 2 7v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1z"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    "shield-check": '<path d="M12 3l8 3v6c0 4.6-3.3 8.3-8 9-4.7-.7-8-4.4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "leaf-deco": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>',
    "linkedin": '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2zM4 2a2 2 0 1 1 0 4 2 2 0 0 1 0-4z"/>',
}


def ic(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICON_PATHS[name]}</svg>'


ARROW = ic("arrow", "arrow")

# image variants discovered on disk: key -> [(width, filename)]
_variants = {}


def _scan_images():
    rx = re.compile(r"^shreya-agro-foods-(.+)-(\d+)\.webp$")
    for f in sorted(os.listdir(IMG_DIR)):
        m = rx.match(f)
        if not m:
            continue
        key, _w = m.group(1), int(m.group(2))
        with Image.open(os.path.join(IMG_DIR, f)) as im:
            _variants.setdefault(key, []).append((im.width, im.height, f))
    for k in _variants:
        _variants[k].sort()


def variants(key):
    if not _variants:
        _scan_images()
    if key not in _variants:
        sys.exit(f"missing image key: {key}")
    return _variants[key]


def img_url(key, which="largest"):
    v = variants(key)
    pick = v[-1] if which == "largest" else v[0]
    return f"/assets/images/{pick[2]}"


POSTERS = {"chicken-meat-masalas", "spice-powders-poster"}  # text-heavy artwork: never crop


def fit_class(key):
    """'fit-contain' for posters, 'pos-low' for tall photos (jars sit low in the frame), '' otherwise."""
    if key in POSTERS:
        return "fit-contain"
    w, h, _ = variants(key)[-1]
    return "pos-low" if h / w > 1.2 else ""


def img(key, alt, sizes="100vw", cls="", lazy=True, fetchpriority=None, extra=""):
    v = variants(key)
    big = v[-1]
    srcset = ", ".join(f"/assets/images/{f} {w}w" for w, _h, f in v)
    classes = (cls + " " + fit_class(key)).strip()
    attrs = f' class="{classes}"' if classes else ""
    if lazy:
        attrs += ' loading="lazy" decoding="async"'
    if fetchpriority:
        attrs += f' fetchpriority="{fetchpriority}"'
    return (f'<img src="/assets/images/{big[2]}" srcset="{srcset}" sizes="{sizes}" alt="{q(alt)}" '
            f'width="{big[0]}" height="{big[1]}"{attrs}{extra}>')


def og_url(key):
    return f"{DOMAIN}/assets/images/og/shreya-agro-foods-{key}.jpg"


def trunc(s, n=158):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


# --------------------------------------------------------------------------------------
# Asset pipeline (minify CSS / JS, cache-busting hash)
# --------------------------------------------------------------------------------------
def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    css = css.replace(";}", "}")
    return css.strip()


def build_assets():
    os.makedirs(os.path.join(ROOT, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets", "js"), exist_ok=True)
    with open(os.path.join(SRC, "style.css"), encoding="utf-8") as fh:
        css = minify_css(fh.read())
    with open(os.path.join(ROOT, "assets", "css", "style.css"), "w", encoding="utf-8") as fh:
        fh.write(css)
    js_src = os.path.join(SRC, "main.js")
    js_out = os.path.join(ROOT, "assets", "js", "main.js")
    done = False
    # Optional: minify JS with esbuild if it's on PATH or pointed to by $ESBUILD (falls back to a plain copy).
    candidates = [[os.environ["ESBUILD"]]] if os.environ.get("ESBUILD") else []
    candidates.append(["esbuild"])
    for cmd in candidates:
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd + [js_src, "--minify", "--target=es2017", f"--outfile={js_out}", "--log-level=error"], check=True)
                done = True
                break
            except Exception:
                pass
    if not done:
        with open(js_src, encoding="utf-8") as fh:
            js = fh.read()
        js = re.sub(r"^\s*/\*.*?\*/\s*", "", js, count=1, flags=re.S)
        with open(js_out, "w", encoding="utf-8") as fh:
            fh.write(js)
    cfg = os.path.join(ROOT, "assets", "js", "config.js")
    if not os.path.exists(cfg):
        with open(cfg, "w", encoding="utf-8") as fh:
            fh.write(CONFIG_JS)
    h = hashlib.md5()
    for p in (os.path.join(ROOT, "assets", "css", "style.css"), js_out):
        with open(p, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()[:8]


CONFIG_JS = """/* Site settings — edit this file directly (no rebuild needed).
 *
 * web3formsKey : free access key from https://web3forms.com (enter your email, the key is emailed to you).
 *                While this is empty, enquiry forms fall back to opening the visitor's email app.
 * gaId         : Google Analytics 4 measurement ID, e.g. "G-XXXXXXXXXX". Leave empty to disable analytics.
 */
window.SHREYA_CONFIG = {
  web3formsKey: "",
  gaId: "",
  email: "info@shreyaagrofoods.com",
  phoneDisplay: "+91 70586 74452",
  phoneTel: "+917058674452",
  whatsapp: "917058674452"
};
"""

ASSET_V = ""  # filled in main()

# --------------------------------------------------------------------------------------
# Layout components
# --------------------------------------------------------------------------------------
NAV = [("Home", "/", "home"), ("About Us", "/about-us/", "about"), ("Products", "/products/", "products"),
       ("Vendor", "/vendor/", "vendor"), ("Contact Us", "/contact-us/", "contact")]


def header(active):
    links = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a>' for label, href, key in NAV
    )
    return f"""<header class="site-header">
<div class="container header-inner">
<a href="/" class="brand" aria-label="{BRAND} — home">
<img src="/assets/images/shreya-agro-foods-logo-160.webp" srcset="/assets/images/shreya-agro-foods-logo-160.webp 160w, /assets/images/shreya-agro-foods-logo-320.webp 320w" sizes="60px" alt="{BRAND} logo" width="60" height="44" fetchpriority="high">
<span class="brand-text"><span class="brand-name"><span class="hide-xs">Shreya </span>Agro Foods Ltd.</span><span class="brand-tagline">{TAGLINE}</span></span>
</a>
<nav class="main-nav" id="mainNav" aria-label="Main navigation">{links}<button type="button" class="btn btn-primary nav-cta" data-enquiry data-type="B2B Enquiry">Enquire Now {ARROW}</button></nav>
<div class="header-actions">
<a class="icon-btn" href="/products/#search" aria-label="Search products">{ic("search")}</a>
<button type="button" class="btn btn-primary btn-sm" data-enquiry data-type="B2B Enquiry">Enquire Now {ARROW}</button>
<button type="button" class="icon-btn nav-toggle" id="navToggle" aria-expanded="false" aria-controls="mainNav" aria-label="Open menu">{ic("menu")}</button>
</div>
</div>
</header>"""


def footer():
    socials = "".join(f'<a href="{u}" target="_blank" rel="noopener noreferrer" aria-label="{BRAND} on {n}">{ic(i)}</a>' for n, u, i in SOCIALS)
    cats = "".join(f'<li><a href="/products/?category={c["slug"]}">{e(c["name"])}</a></li>' for c in CATEGORIES)
    return f"""<footer class="site-footer">
<div class="container">
<div class="footer-grid">
<div class="footer-brand">
<img src="/assets/images/shreya-agro-foods-logo-160.webp" alt="{BRAND} logo" width="160" height="116" loading="lazy" style="width:auto;height:48px">
<p>{TAGLINE} Quality FMCG food products from Mumbai, supplied to businesses across India.</p>
<div class="socials">{socials}</div>
</div>
<nav aria-label="Quick links"><h2>Quick Links</h2><ul>
<li><a href="/">Home</a></li><li><a href="/about-us/">About Us</a></li><li><a href="/products/">Products</a></li>
<li><a href="/vendor/">Vendor / B2B Partner</a></li><li><a href="/contact-us/">Contact Us</a></li><li><a href="/contact-us/#careers">Careers</a></li>
</ul></nav>
<nav aria-label="Product categories"><h2>Our Products</h2><ul>{cats}</ul></nav>
<div><h2>Contact</h2><ul class="footer-contact">
<li>{ic("pin")}<span>{ADDRESS}</span></li>
<li>{ic("phone")}<a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
<li>{ic("mail")}<a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li>{ic("clock")}<span>Mon–Fri 10am–6pm<br>Sat 10am–2pm</span></li>
</ul></div>
</div>
<div class="footer-bottom"><span>&copy; {YEAR} {COMPANY} All rights reserved.</span><span>Mumbai, Maharashtra, India</span><span>Designed & Managed by <a href="https://tcongsinfotech.com/" target="_blank" rel="noopener noreferrer">Tcongs Infotech</a></span></div>
</div>
</footer>"""


def _wrap(icon, control):
    return f'<div class="input-wrap">{ic(icon)}{control}</div>' if icon else control


def field(label, name, ftype="text", required=False, placeholder="", fid=None, autocomplete=None, extra="", icon=None):
    fid = fid or name
    req = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    r = " required" if required else ""
    ac = f' autocomplete="{autocomplete}"' if autocomplete else ""
    inputmode = ' inputmode="tel"' if ftype == "tel" else ""
    control = f'<input type="{ftype}" id="{fid}" name="{name}"{r} placeholder="{q(placeholder)}"{ac}{inputmode} aria-describedby="{fid}_err"{extra}>'
    return (f'<div class="field"><label for="{fid}">{label}{req}</label>{_wrap(icon, control)}'
            f'<p class="field-error" id="{fid}_err" role="alert" hidden></p></div>')


def textarea(label, name, required=False, placeholder="", fid=None, rows=3, icon=None):
    fid = fid or name
    req = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    r = " required" if required else ""
    control = f'<textarea id="{fid}" name="{name}" rows="{rows}"{r} placeholder="{q(placeholder)}" aria-describedby="{fid}_err"></textarea>'
    return (f'<div class="field"><label for="{fid}">{label}{req}</label>{_wrap(icon, control)}'
            f'<p class="field-error" id="{fid}_err" role="alert" hidden></p></div>')


def select(label, name, options, required=False, fid=None, placeholder="Select an option", icon=None):
    fid = fid or name
    req = ' <span class="req" aria-hidden="true">*</span>' if required else ""
    r = " required" if required else ""
    opts = f'<option value="">{e(placeholder)}</option>' + "".join(f'<option value="{q(o)}">{e(o)}</option>' for o in options)
    control = f'<select id="{fid}" name="{name}"{r} aria-describedby="{fid}_err">{opts}</select>'
    return (f'<div class="field"><label for="{fid}">{label}{req}</label>{_wrap(icon, control)}'
            f'<p class="field-error" id="{fid}_err" role="alert" hidden></p></div>')


HONEYPOT = '<div class="hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="botcheck" tabindex="-1" autocomplete="off"></label></div>'


def submit_btn(label):
    return f'<button type="submit" class="btn btn-primary btn-block" data-label="{q(label)}"><span class="label">{e(label)}</span> {ARROW}</button>'


def success_box(sid, title="Thank You!", text="Your enquiry has been received successfully. Our B2B team will contact you shortly.", close=False):
    btn = '<button type="button" class="btn btn-primary" data-close-modal>Close</button>' if close else ""
    return (f'<div class="success-box" id="{sid}" hidden data-fallback-title="Almost there!" '
            f'data-fallback-text="Your email app has opened with your details pre-filled. Please press Send to complete your enquiry.">'
            f'<div class="check">{ic("check")}</div><h3>{e(title)}</h3><p>{e(text)}</p>{btn}</div>')


ENQUIRY_TYPES = ["Product Enquiry", "B2B / Wholesale", "Distribution", "Business Partnership", "General Enquiry", "Career"]


def enquiry_modal():
    prod_opts = [p["name"] for p in PRODUCTS]
    return f"""<div class="modal" id="enquiryModal" hidden>
<div class="modal-backdrop" data-close-modal></div>
<div class="modal-dialog no-aside" role="dialog" aria-modal="true" aria-labelledby="enquiryTitle">
<button type="button" class="modal-close" data-close-modal aria-label="Close enquiry form">{ic("close")}</button>
<aside class="modal-aside" id="enquiryAside" hidden>
<img id="enquiryAsideImg" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" alt="" width="320" height="320" hidden>
<h3 id="enquiryAsideName"></h3>
<p id="enquiryAsideDesc"></p>
<div class="pack-tags" id="enquiryAsidePacks"></div>
</aside>
<div class="modal-main">
<div id="enquiryFormWrap">
<h2 id="enquiryTitle">B2B Product Enquiry</h2>
<p id="enquiryIntro"></p>
<p class="enquiry-for" id="enquiryProductField" hidden><strong>Enquiry For:</strong> <span id="enquiryProductName"></span></p>
<form id="enquiryForm" data-form="enquiry" data-wrap="enquiryFormWrap" data-success="enquirySuccess" data-subject="B2B enquiry — Shreya Agro Foods website" action="#">
<input type="hidden" name="enquiry_type" id="enquiryType" value="B2B Enquiry">
<input type="hidden" name="product" id="enquiryProduct" value="">
{HONEYPOT}
<div class="field-row">{field("Name", "name", required=True, placeholder="Enter your name", fid="eq_name", autocomplete="name")}{field("Company Name", "company", placeholder="Enter company name", fid="eq_company", autocomplete="organization")}</div>
<div class="field-row">{field("Location", "location", required=True, placeholder="City / State", fid="eq_location", autocomplete="address-level2")}{field("Mobile Number", "mobile", "tel", required=True, placeholder="+91 XXXXX XXXXX", fid="eq_mobile", autocomplete="tel")}</div>
{field("Email", "email", "email", placeholder="Enter email", fid="eq_email", autocomplete="email")}
<div id="enquiryProductSelectWrap">{select("Product / Requirement", "product_interest", prod_opts + ["Multiple products", "Other"], fid="enquiryProductSelect", placeholder="Select a product (optional)")}</div>
{textarea("Requirement / Quantity", "message", placeholder="Tell us about your requirement", fid="eq_message")}
<p class="form-status" role="alert" hidden></p>
{submit_btn("Submit B2B Enquiry")}
<p class="form-note">We respect your privacy. Your details are only used to respond to your enquiry.</p>
</form>
</div>
{success_box("enquirySuccess", close=True)}
</div>
</div>
</div>"""


def apply_modal():
    return f"""<div class="modal" id="applyModal" hidden>
<div class="modal-backdrop" data-close-modal></div>
<div class="modal-dialog narrow" role="dialog" aria-modal="true" aria-labelledby="applyTitle">
<button type="button" class="modal-close" data-close-modal aria-label="Close application form">{ic("close")}</button>
<div class="modal-main">
<div id="applyFormWrap">
<h2 id="applyTitle">Apply for this Position</h2>
<p class="enquiry-for"><strong>Position:</strong> <span id="applyPosition"></span></p>
<form id="applyForm" data-form="apply" data-wrap="applyFormWrap" data-success="applySuccess" data-subject="Job application — Shreya Agro Foods website" action="#">
<input type="hidden" name="position" id="applyPositionInput" value="">
{HONEYPOT}
{field("Full Name", "name", required=True, placeholder="Enter your name", fid="ap_name", autocomplete="name")}
<div class="field-row">{field("Mobile Number", "mobile", "tel", required=True, placeholder="Enter mobile number", fid="ap_mobile", autocomplete="tel")}{field("Email", "email", "email", required=True, placeholder="Enter email", fid="ap_email", autocomplete="email")}</div>
<div class="field-row">{field("Current Location", "location", required=True, placeholder="City", fid="ap_location", autocomplete="address-level2")}{field("Experience", "experience", placeholder="Years of experience", fid="ap_exp")}</div>
<div class="field"><label for="ap_resume">Resume <span class="req" aria-hidden="true">*</span></label><input type="file" id="ap_resume" name="resume" required accept=".pdf,.doc,.docx" aria-describedby="ap_resume_err"><p class="field-error" id="ap_resume_err" role="alert" hidden></p></div>
{textarea("Message", "message", placeholder="Tell us briefly about yourself...", fid="ap_message")}
<p class="form-status" role="alert" hidden></p>
{submit_btn("Submit Application")}
<p class="form-note">PDF or DOC, up to 5 MB.</p>
</form>
</div>
<div class="success-box" id="applySuccess" hidden data-fallback-title="Almost there!" data-fallback-text="Your email app has opened with your details pre-filled. Please attach your resume and press Send to complete your application.">
<div class="check">{ic("check")}</div><h3>Application Submitted Successfully!</h3>
<p>Thank you for your interest in joining Shreya Agro Foods. Our team will review your application and contact you if your profile matches an available opportunity.</p>
<button type="button" class="btn btn-primary" data-close-modal>Close</button></div>
</div>
</div>
</div>"""


def chatbot():
    return f"""<button type="button" class="chat-fab" id="chatFab" aria-expanded="false" aria-controls="chatPanel" aria-label="Chat with us — how can we help?">{ic("bot")}<span class="dot"></span></button>
<div class="chat-panel" id="chatPanel" role="dialog" aria-label="Chat assistant" hidden>
<div class="chat-head"><div><strong>{BRAND}</strong><span>How can we help?</span></div><button type="button" class="icon-btn" id="chatClose" aria-label="Close chat">{ic("close")}</button></div>
<div class="chat-body" id="chatBody" aria-live="polite"></div>
</div>"""


def jsonld(*nodes):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": list(nodes)}, ensure_ascii=False, separators=(",", ":")) + "</script>"


ORG_NODE = {
    "@type": "Organization", "@id": DOMAIN + "/#organization", "name": COMPANY, "alternateName": BRAND, "url": DOMAIN + "/",
    "logo": DOMAIN + "/assets/images/shreya-agro-foods-icon-192.png",
    "email": EMAIL, "telephone": "+91-70586-74452",
    "address": {"@type": "PostalAddress", "streetAddress": "411-412, Mastermind Rd, Royal Palms, Aarey Milk Colony, Goregaon East",
                "addressLocality": "Mumbai", "addressRegion": "Maharashtra", "postalCode": "400065", "addressCountry": "IN"},
    "contactPoint": [{"@type": "ContactPoint", "telephone": "+91-70586-74452", "email": EMAIL, "contactType": "sales", "areaServed": "IN", "availableLanguage": ["English", "Hindi"]}],
    "sameAs": [u for _n, u, _i in SOCIALS],
}
WEBSITE_NODE = {"@type": "WebSite", "@id": DOMAIN + "/#website", "name": BRAND, "url": DOMAIN + "/", "publisher": {"@id": DOMAIN + "/#organization"}}


def breadcrumb_node(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(items)]}


PAGES = []  # (url_path, priority) for sitemap


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)


def page(path, *, title, desc, body, active="", og_key="hero-desktop", schema="", noindex=False, canonical=None,
         body_attrs="", preload="", extra_modals="", sitemap_priority=None):
    url = "/" if path == "index.html" else "/" + path.replace("index.html", "")
    canon = canonical or (DOMAIN + url)
    if sitemap_priority is not None and not noindex:
        PAGES.append((url, sitemap_priority))
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    og_img = og_url(og_key)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{q(desc)}">
{robots}
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#1c5b3f">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{q(title)}">
<meta property="og:description" content="{q(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{q(title)}">
<meta name="twitter:description" content="{q(desc)}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/images/shreya-agro-foods-icon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/images/shreya-agro-foods-icon-192.png">
<link rel="apple-touch-icon" href="/assets/images/shreya-agro-foods-apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/plus-jakarta-sans-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/playfair-display.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<link rel="stylesheet" href="/assets/css/style.css?v={ASSET_V}">
{schema}
</head>
<body{(" " + body_attrs) if body_attrs else ""}>
<a class="skip-link" href="#main">Skip to main content</a>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
{enquiry_modal()}
{extra_modals}
{chatbot()}
<script src="/assets/js/config.js?v={ASSET_V}" defer></script>
<script src="/assets/js/main.js?v={ASSET_V}" defer></script>
</body>
</html>
"""
    write(path, doc)


# --------------------------------------------------------------------------------------
# Reusable sections
# --------------------------------------------------------------------------------------
def section_head(eyebrow, h2, p="", center=False, split_link=None):
    cls = "section-head" + (" center" if center else "") + (" split-head" if split_link else "")
    link = f'<a class="link-arrow" href="{split_link[1]}">{split_link[0]} {ARROW}</a>' if split_link else ""
    para = f"<p>{p}</p>" if p else ""
    inner = f'<div><span class="eyebrow">{e(eyebrow)}</span><h2>{h2}</h2>{para}</div>{link}'
    if not split_link:
        inner = f'<span class="eyebrow">{e(eyebrow)}</span><h2>{h2}</h2>{para}'
    return f'<div class="{cls}">{inner}</div>'


def category_card(c, lazy=True):
    n = sum(1 for p in PRODUCTS if p["cat"] == c["slug"])
    bg1, bg2 = c["bg"].split(",")
    media_cls = "cat-media blend" if c["blend"] else "cat-media"
    return (f'<a class="cat-card" href="/products/?category={c["slug"]}" aria-label="{q(c["name"])} — {n} product{"s" if n != 1 else ""}" '
            f'style="--bg1:{bg1};--bg2:{bg2};--ink:{c["ink"]};--badge:{c["badge"]}">'
            f'<div class="cat-text"><span class="cat-badge">{ic(c["icon"])}</span><h3>{e(c["name"])}</h3><p>{e(c["desc"])}</p>'
            f'<span class="cat-btn">View Products {ARROW}</span></div>'
            f'<div class="{media_cls}">{img(c["img"], f"{BRAND} {c["name"]}", sizes="(min-width:1100px) 190px, (min-width:640px) 220px, 46vw", lazy=lazy)}</div></a>')


def category_grid(lazy=True):
    return '<div class="cat-grid">' + "".join(category_card(c, lazy=lazy) for c in CATEGORIES) + "</div>"


def product_card(p, lazy=True):
    key, _alt = p["images"][0]
    cat = CAT[p["cat"]]
    search = f'{p["name"]} {p["short"]} {cat["name"]} {p["type"]}'.lower()
    packs = p["packs"] or ""
    return (f'<article class="product-card" data-category="{p["cat"]}" data-type="{q(p["type"])}" data-search="{q(search)}">'
            f'<a class="product-media" href="/products/{p["slug"]}/" tabindex="-1" aria-hidden="true">{img(key, f"{BRAND} {p["name"]}", sizes="(min-width:1100px) 280px, (min-width:800px) 31vw, 46vw", lazy=lazy)}</a>'
            f'<div class="product-body"><h3><a href="/products/{p["slug"]}/">{e(p["name"])}</a></h3>'
            f'<p class="product-desc">{e(p["short"])}</p>'
            f'<p class="product-meta"><strong>Available for:</strong> B2B | Wholesale | Distribution</p>'
            f'<div class="product-actions"><button type="button" class="enquire-btn" data-enquiry data-product="{q(p["name"])}" '
            f'data-image="{img_url(key, "smallest")}" data-desc="{q(p["short"])}" data-packs="{q(packs)}" data-type="Product Enquiry">'
            f'Product Enquiry {ARROW}</button></div></div></article>')


def cta_band(h2, p, primary_label="Make a B2B Enquiry", secondary=("Talk to Our Team", "/contact-us/"), full=False):
    cls = "cta-full" if full else "cta-band"
    inner = (f'<h2>{h2}</h2><p>{p}</p><div class="hero-actions">'
             f'<button type="button" class="btn btn-light" data-enquiry data-type="B2B Enquiry">{primary_label} {ARROW}</button>'
             f'<a class="btn btn-outline-light" href="{secondary[1]}">{secondary[0]}</a></div>')
    if full:
        return f'<section class="{cls}"><div class="container">{inner}</div></section>'
    return f'<section class="section"><div class="container"><div class="{cls}">{inner}</div></div></section>'


def feature_cards(items, cols="grid-4 feature-grid"):
    cards = "".join(
        f'<div class="feature-card"><div class="icon">{ic(i)}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, t, d in items)
    return f'<div class="grid {cols}">{cards}</div>'


# --------------------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------------------
def build_home():
    hero_pre = ('<link rel="preload" as="image" href="/assets/images/shreya-agro-foods-hero-mobile-640.webp" media="(max-width: 767px)" fetchpriority="high">\n'
                '<link rel="preload" as="image" imagesrcset="/assets/images/shreya-agro-foods-hero-desktop-1200.webp 1200w, /assets/images/shreya-agro-foods-hero-desktop-1800.webp 1800w" imagesizes="100vw" media="(min-width: 768px)" fetchpriority="high">')
    hero = f"""<section class="hero" aria-labelledby="hero-title">
<picture class="hero-media">
<source media="(max-width: 767px)" srcset="/assets/images/shreya-agro-foods-hero-mobile-640.webp 640w, /assets/images/shreya-agro-foods-hero-mobile-887.webp 887w" sizes="100vw">
<source media="(min-width: 768px)" srcset="/assets/images/shreya-agro-foods-hero-desktop-1200.webp 1200w, /assets/images/shreya-agro-foods-hero-desktop-1800.webp 1800w" sizes="100vw">
<img src="/assets/images/shreya-agro-foods-hero-desktop-1200.webp" alt="Shreya Agro Foods products — jam, masala and spices in front of the Shreya manufacturing facility" width="1200" height="400" fetchpriority="high" decoding="async">
</picture>
<div class="container hero-inner"><div class="hero-copy">
<span class="eyebrow">Shreya Agro Foods Ltd. · Mumbai</span>
<h1 id="hero-title">Quality FMCG Products Built on Trust</h1>
<p class="lead">Delivering authentic taste and trusted quality for over 26 years.</p>
<div class="hero-actions"><a class="btn btn-accent" href="/products/">Explore Our Products {ARROW}</a><a class="btn btn-outline-light" href="/vendor/">Become a B2B Partner</a></div>
<ul class="hero-trust"><li>{ic("shield")}Quality assured</li><li>{ic("truck")}Reliable B2B supply</li><li>{ic("globe")}Pan India reach</li></ul>
</div></div>
</section>"""
    stats = """<section class="stats-strip" aria-label="Shreya Agro Foods at a glance"><div class="container stats-grid">
<div class="stat"><strong>26+</strong><span>Years of FMCG experience</span></div>
<div class="stat"><strong>Pan India</strong><span>Market presence</span></div>
<div class="stat"><strong>7</strong><span>Countries &amp; growing</span></div>
<div class="stat"><strong>B2B</strong><span>Wholesale &amp; distribution</span></div>
</div></section>"""
    cats = f"""<section class="section cats-section" id="categories"><div class="container"><div class="cat-panel">
{ic("leaf-deco", "leaf-deco")}
<div class="cat-head"><div><span class="eyebrow with-line">Our Product Categories</span>
<h2>A World of Flavours, <span class="script">Under One Roof</span></h2>
<p>From everyday meals to festive celebrations, our wide range of products brings flavour, nutrition and tradition to your table.</p></div>
<a class="pill-link" href="/products/">View All Products {ARROW}</a></div>
{category_grid()}
</div></div></section>"""
    popular = (f'<section class="section section-alt"><div class="container">'
               + section_head("Our Popular Products", "Loved for Their Taste, Trusted for Their Quality",
                              "A few favourites from our catalogue. Every product is available for B2B, wholesale and distribution enquiries.",
                              split_link=("Explore our FMCG products", "/products/"))
               + '<div class="product-grid">' + "".join(product_card(PROD[s]) for s in POPULAR) + '</div></div></section>')
    quality = f"""<section class="section quality-section"><div class="container two-col">
<div class="media-frame">{img("quality-facility", "Shreya Agro Foods quality team inspecting jars on the production line", sizes="(min-width:860px) 560px, 92vw")}</div>
<div>
<span class="eyebrow with-dot">Our Commitment</span>
<h2>Quality You Can Trust</h2>
<p>Every product is crafted with care, using 100% natural ingredients, subjected to rigorous lab-tested purity, and released only when it meets our highest standards of taste, nutrition and safety.</p>
<ul class="icon-row">
<li><span class="icon">{ic("leaf")}</span>100% Natural Ingredients</li>
<li><span class="icon">{ic("flask")}</span>Rigorous Quality Testing</li>
<li><span class="icon">{ic("factory")}</span>Modern Production Facilities</li>
<li><span class="icon">{ic("sprout")}</span>Authentic Taste &amp; Nutrition</li>
<li><span class="icon">{ic("shield")}</span>Food Safety &amp; Purity</li>
</ul>
<p style="margin-top:24px"><a class="btn btn-outline" href="/about-us/">Learn about Shreya Agro Foods {ARROW}</a></p>
</div></div></section>"""
    countries = [("India", "IN", "in.svg"), ("Nepal", "NP", "np.svg"), ("Bangladesh", "BD", "bd.svg"), ("Bhutan", "BT", "bt.webp"),
                 ("UAE", "AE", "ae.svg"), ("South Africa", "ZA", "za.svg"), ("Canada", "CA", "ca.svg")]
    nodes = "".join(
        f'<li style="--a:{round(i * 360 / len(countries), 2)}deg" data-name="{n}" data-flag="/assets/flags/{f}"><span class="orbit-pos"><span class="orbit-node">'
        f'<b>{code}</b><span class="orbit-label">{n}</span></span></span></li>'
        for i, (n, code, f) in enumerate(countries))
    global_sec = f"""<section class="section on-dark global-sec"><div class="container two-col">
<div>
<span class="eyebrow with-dot">Global Presence</span>
<h2>From India to the World</h2>
<p>Our products are enjoyed in Nepal, Bangladesh, Bhutan, UAE, South Africa, Canada and beyond, with ambitious expansion plans to reach more homes worldwide.</p>
<p><a class="btn btn-ghost" href="/contact-us/">Our Global Reach {ARROW}</a></p>
</div>
<div class="orbit-wrap"><div class="orbit" id="orbit" role="img" aria-label="Shreya Agro Foods products are enjoyed in India, Nepal, Bangladesh, Bhutan, UAE, South Africa and Canada">
<span class="orbit-glow" aria-hidden="true"></span><span class="orbit-ring" aria-hidden="true"></span><span class="orbit-ring dashed" aria-hidden="true"></span>
<ul class="orbit-track" aria-hidden="true">{nodes}</ul>
<span class="orbit-line" aria-hidden="true"></span>
<div class="orbit-tip" aria-hidden="true"><strong id="orbitTipName">Canada</strong><img id="orbitTipFlag" src="/assets/flags/ca.svg" alt="" width="20" height="15"><small>Connection Established</small></div>
<div class="orbit-center"><span class="orbit-globe" aria-hidden="true"></span><strong>7 Countries</strong><span>&amp; Growing</span></div>
</div></div>
</div></section>"""
    cta = cta_band("Bring Shreya to Your Market", "Partner with us for distribution and business opportunities across India and beyond.",
                   secondary=("Contact Us", "/contact-us/"))
    schema = jsonld(ORG_NODE, WEBSITE_NODE)
    page("index.html", title="Shreya Agro Foods | FMCG Products & Food Manufacturer in India",
         desc="Shreya Agro Foods is an FMCG company with 26+ years of experience, offering quality food products and B2B business opportunities across India.",
         body=hero + stats + cats + popular + quality + global_sec + cta, active="home", schema=schema, preload=hero_pre,
         og_key="hero-desktop", sitemap_priority="1.0")


def build_about():
    hero = f"""<section class="page-hero has-image center" style="--hero-img:url(/assets/images/shreya-agro-foods-hero-desktop-1200.webp)"><div class="container">
<span class="eyebrow">About Shreya Agro Foods</span>
<h1>26+ Years of Building Trust Through Quality</h1>
<p class="lead">From our roots in Mumbai to becoming a trusted name in the FMCG industry, Shreya Agro Foods has been driven by a simple vision — to create quality food products that become a part of everyday lives.</p>
<div class="hero-actions"><a class="btn btn-accent" href="/products/">Explore Our Products {ARROW}</a><a class="btn btn-outline-light" href="/vendor/">Become a B2B Partner</a></div>
</div></section>"""
    intro = f"""<section class="section"><div class="container two-col">
<div class="media-frame">{img("quality-facility", "Shreya Agro Foods production line with quality team", sizes="(min-width:860px) 560px, 92vw")}</div>
<div>
<h2>A Legacy Built on Quality &amp; Trust</h2>
<p>Shreya Agro Foods Ltd. is one of India's leading FMCG companies, with a legacy spanning over 26 years.</p>
<p>Rooted in Mumbai, the company was built with an entrepreneurial vision and a passion for delivering quality food products to consumers across markets.</p>
<p>Over the years, Shreya Agro Foods has grown through a strong commitment to quality, innovation, customer satisfaction and long-term relationships.</p>
<div class="stat-row"><div><strong>26+</strong><span>Years of Experience</span></div><div><strong>Pan India</strong><span>Market Presence</span></div><div><strong>Quality First</strong><span>Our Commitment</span></div></div>
<p style="margin-top:26px"><a class="link-arrow" href="/products/">Explore our FMCG products {ARROW}</a></p>
</div></div></section>"""
    vm = f"""<section class="section section-alt"><div class="container grid grid-2">
<div class="vm-card"><div class="icon">{ic("eye")}</div><h2>Our Vision</h2><p>To build a trusted FMCG brand that brings quality, innovation and value to consumers across India and beyond.</p></div>
<div class="vm-card alt"><div class="icon">{ic("target")}</div><h2>Our Mission</h2><p>To consistently deliver high-quality products while building lasting relationships with customers, partners and communities.</p></div>
</div></section>"""
    why = ('<section class="section"><div class="container">'
           + section_head("Why Shreya Agro Foods?", "What Sets Us Apart", center=True)
           + feature_cards([
               ("award", "Quality Driven", "Quality at every stage, from sourcing to final product."),
               ("users", "Customer Focused", "Understanding customer needs and continuously improving."),
               ("bulb", "Innovation", "Creating products that meet changing consumer preferences."),
               ("shield", "Trusted Relationships", "Building long-term partnerships with distributors, retailers and businesses."),
           ]) + "</div></section>")
    steps = [("1999", "Company begins its journey", "spices-still-life", "Spices and ingredients that started the Shreya journey"),
             ("Growth", "Expanding products and market presence", "spice-powder-collection", "Shreya spice powder range"),
             ("Expansion", "Building stronger distribution networks", "mango-mix-pickle-display", "Shreya pickles ready for distribution"),
             ("Today", "A growing FMCG company serving diverse markets", "wheat-flour-kitchen", "Shreya wheat flour and everyday staples")]
    tl = "".join(
        f'<li class="tl-item"><div class="tl-dot" aria-hidden="true">{i + 1}</div><h3>{y}</h3><p>{e(t)}</p>{img(k, f"{BRAND} — {a}", sizes="(min-width:900px) 260px, 360px")}</li>'
        for i, (y, t, k, a) in enumerate(steps))
    journey = ('<section class="section section-tint"><div class="container">'
               + section_head("Our Journey", "From a Mumbai Start-up to a Growing FMCG Company", center=True)
               + f'<ol class="timeline" style="list-style:none;margin:0;padding:0">{tl}</ol></div></section>')
    tiles = [("hero-mobile", "Manufacturing", "Shreya manufacturing facility surrounded by greenery", "640"),
             ("quality-facility", "Quality checking", "Quality inspection on the production line", ""),
             ("besan-chakki-atta", "Packaging", "Packaged Shreya Besan Chakki Ka Atta", ""),
             ("mango-mix-pickle-display", "Finished products", "Finished Shreya mango and mix pickle jars", "")]
    tile_html = "".join(f'<figure class="quality-tile">{img(k, a, sizes="(min-width:900px) 280px, 46vw")}<figcaption>{t}</figcaption></figure>' for k, t, a, _ in tiles)
    quality = ('<section class="section on-dark"><div class="container">'
               + section_head("Quality & Manufacturing", "Quality Is at the Heart of Everything We Do",
                              "We believe quality is not just a standard — it is a responsibility. From raw material selection to manufacturing, packaging and distribution, we focus on maintaining consistent quality across every product.")
               + f'<div class="quality-grid">{tile_html}</div></div></section>')
    cta = cta_band("Looking for a Reliable FMCG Partner?", "Partner with Shreya Agro Foods for quality products, reliable supply and long-term business opportunities.",
                   secondary=("Contact Us", "/contact-us/"))
    page("about-us/index.html", title="About Shreya Agro Foods | 26+ Years of FMCG Experience",
         desc="Shreya Agro Foods is a Mumbai-rooted FMCG company with 26+ years of experience in quality food products, reliable supply and long-term B2B partnerships.",
         body=hero + intro + vm + why + journey + quality + cta, active="about", og_key="hero-desktop", sitemap_priority="0.8",
         schema=jsonld(ORG_NODE, breadcrumb_node([("Home", "/"), ("About Us", "/about-us/")])))


def build_products():
    hero = f"""<section class="page-hero"><div class="container">
<span class="eyebrow">Products</span>
<h1>Our FMCG Products</h1>
<p class="lead"><strong>Quality Products for Every Market.</strong> Explore our range of FMCG products, created with a focus on quality, consistency and customer satisfaction.</p>
<div class="hero-actions"><a class="btn btn-accent" href="#all-products">View All Products {ARROW}</a><a class="btn btn-outline-light" href="/vendor/">Become a B2B Partner</a></div>
</div></section>"""
    cats = ('<section class="section" id="categories"><div class="container">'
            + section_head("Product Categories", "Explore Our Product Categories", "Choose a category to browse the products inside it.")
            + category_grid() + '</div></section>')
    chips = '<button type="button" class="chip" data-filter="all" aria-pressed="true">All Products</button>' + "".join(
        f'<button type="button" class="chip" data-filter="{c["slug"]}" aria-pressed="false">{e(c["name"])}</button>' for c in CATEGORIES)
    listing = f"""<section class="section section-alt" id="all-products"><div class="container">
{section_head("Product Catalogue", "Our Products", "Search by name or filter by category. Every product is available for B2B, wholesale and distribution — use Product Enquiry to reach our team.")}
<div class="filter-bar" role="search">
<div class="filter-top">
<div class="search-box"><label class="visually-hidden" for="productSearch">Search products</label>{ic("search")}<input type="search" id="productSearch" placeholder="Search by product name..." autocomplete="off"></div>
<div><label class="visually-hidden" for="subcategory">Sub-category</label><select id="subcategory"><option value="all">All sub-categories</option></select></div>
</div>
<div class="chips" role="group" aria-label="Filter by category">{chips}</div>
<p class="result-count" id="resultCount" aria-live="polite">{len(PRODUCTS)} products</p>
</div>
<div class="product-grid" id="productGrid">{"".join(product_card(p) for p in PRODUCTS)}</div>
<div class="no-results" id="noResults" hidden><h3>No products found</h3><p>Try a different search term or category, or tell us what you need and we will help.</p>
<p><button type="button" class="btn btn-outline" id="resetFilters">Clear filters</button> <button type="button" class="btn btn-primary" data-enquiry data-type="Product Enquiry" data-title="Product Enquiry">Send a Product Enquiry</button></p></div>
</div></section>"""
    cta = cta_band("Looking for Bulk FMCG Products?", "Connect with Shreya Agro Foods for wholesale, distribution and business enquiries.",
                   secondary=("Talk to Our Team", "/contact-us/"), full=True)
    schema = jsonld(ORG_NODE, breadcrumb_node([("Home", "/"), ("Products", "/products/")]), {
        "@type": "ItemList", "name": "Shreya Agro Foods products",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{DOMAIN}/products/{p['slug']}/", "name": p["name"]} for i, p in enumerate(PRODUCTS)]})
    page("products/index.html", title="FMCG Products | Shreya Agro Foods",
         desc="Browse the Shreya Agro Foods FMCG range — masalas, pickles, sweets, jams, flour, rice and bakery — for B2B, wholesale and distribution enquiries.",
         body=hero + cats + listing + cta, active="products", og_key="hero-desktop", sitemap_priority="0.9", schema=schema)


def build_product(p):
    cat = CAT[p["cat"]]
    keys = p["images"]
    main_key, main_alt = keys[0]
    packs_txt = p["packs"] or "On enquiry"
    fit = " " + fit_class(main_key)
    v = variants(main_key)
    main_img = (f'<img id="galleryMain" class="{fit.strip()}" src="/assets/images/{v[-1][2]}" '
                f'srcset="{", ".join(f"/assets/images/{f} {w}w" for w, _h, f in v)}" sizes="(min-width:860px) 560px, 92vw" '
                f'alt="{q(BRAND + " " + p["name"])}" width="{v[-1][0]}" height="{v[-1][1]}" fetchpriority="high" decoding="async">')
    thumbs = ""
    if len(keys) > 1:
        tb = ""
        for i, (k, a) in enumerate(keys):
            vv = variants(k)
            fc = fit_class(k)
            f = {"fit-contain": "contain", "pos-low": "low"}.get(fc, "cover")
            srcset = ", ".join(f"/assets/images/{fn} {w}w" for w, _h, fn in vv)
            cur = ' aria-current="true"' if i == 0 else ""
            tb += (f'<button type="button" data-src="/assets/images/{vv[-1][2]}" data-srcset="{srcset}" data-alt="{q(BRAND + " " + p["name"] + " — " + a)}" data-fit="{f}"{cur} aria-label="Show image {i + 1}: {q(a)}">'
                   f'<img src="/assets/images/{vv[0][2]}" alt="" width="{vv[0][0]}" height="{vv[0][1]}" loading="lazy" class="{fc}"></button>')
        thumbs = f'<div class="gallery-thumbs" role="group" aria-label="Product images">{tb}</div>'
    about2 = (f'{e(p["name"])} is part of the {BRAND} range of {e(cat["name"].lower())}, offered to distributors, wholesalers and retailers across India. '
              f'Share your requirement and our B2B team will respond with availability and supply details.')
    specs = [("Category", cat["name"]), ("Product Type", p["type"]), ("Pack Size", packs_txt), ("Available For", "B2B / Wholesale / Distribution"),
             ("MOQ", "On Enquiry"), ("Brand", BRAND)]
    spec_rows = "".join(f"<tr><th scope='row'>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in specs)
    highlights = ["Supplied to distributors, wholesalers and retailers", "Hygienically packed", "Pack sizes and MOQ shared on enquiry" if not p["packs"] else f'Pack sizes: {e(p["packs"])}', f"Made by {COMPANY}, Mumbai"]
    hl = "".join(f"<li>{h}</li>" for h in highlights)
    related = [x for x in PRODUCTS if x["cat"] == p["cat"] and x["slug"] != p["slug"]]
    related += [x for x in PRODUCTS if x["cat"] != p["cat"] and x["slug"] != p["slug"]]
    related = related[:4]
    rel_cards = "".join(
        f'<a class="category-card" href="/products/{r["slug"]}/"><div class="category-media" style="aspect-ratio:1/1;background:#fff">{img(r["images"][0][0], f"{BRAND} {r["name"]}", sizes="(min-width:992px) 280px, 46vw")}</div>'
        f'<div class="category-body"><h3 style="font-size:1.02rem">{e(r["name"])}</h3><span class="link-arrow">View Product {ARROW}</span></div></a>' for r in related)
    body = f"""<div class="container"><nav class="breadcrumb" aria-label="Breadcrumb"><ol>
<li><a href="/">Home</a></li><li><a href="/products/">Products</a></li><li><a href="/products/?category={cat["slug"]}">{e(cat["name"])}</a></li><li><span aria-current="page">{e(p["name"])}</span></li>
</ol></nav></div>
<section class="section" style="padding-top:12px"><div class="container pd-grid">
<div><div class="gallery-main">{main_img}</div>{thumbs}</div>
<div class="pd-info">
<span class="badge">{e(cat["name"])}</span>
<h1>{e(p["name"])}</h1>
<p class="lead">{e(p["short"])}</p>
<table class="spec-table"><caption>Product Information</caption><tbody>{spec_rows}</tbody></table>
<div class="pd-actions">
<button type="button" class="btn btn-primary" data-enquiry data-product="{q(p["name"])}" data-image="{img_url(main_key, "smallest")}" data-desc="{q(p["short"])}" data-packs="{q(p["packs"])}" data-type="Product Enquiry">Enquire Now {ARROW}</button>
<a class="btn btn-outline" href="/contact-us/">Talk to Our Team</a>
</div>
<p class="form-note" style="text-align:left">B2B catalogue — no online prices. Pricing and availability are shared on enquiry.</p>
</div></div></section>
<section class="section section-alt"><div class="container two-col" style="align-items:start">
<div><span class="eyebrow">About this product</span><h2>{e(p["name"])}</h2><p>{about2}</p><p>Pricing, MOQ and delivery terms are shared on enquiry. Use <strong>Enquire Now</strong> and our B2B team will respond with the details.</p></div>
<div class="feature-card"><h3>Key details</h3><ul class="check-list" style="margin-top:14px">{hl}</ul></div>
</div></section>
<section class="section"><div class="container">
{section_head("Why Choose This Product?", "Built for B2B Buyers", center=True)}
{feature_cards([("award", "Quality Assured", "Consistent quality standards."), ("truck", "Reliable Supply", "Designed for regular B2B requirements."), ("package", "Market Ready", "Products suitable for diverse markets."), ("headset", "B2B Support", "Dedicated enquiry and business support.")])}
</div></section>
<section class="section section-alt"><div class="container">
{section_head("Related Products", "You May Also Be Interested In", split_link=("Explore all FMCG products", "/products/"))}
<div class="grid grid-4">{rel_cards}</div>
</div></section>
{cta_band("Looking for Bulk FMCG Products?", "Connect with Shreya Agro Foods for wholesale, distribution and business enquiries.", secondary=("Talk to Our Team", "/contact-us/"), full=True)}"""
    url = f"{DOMAIN}/products/{p['slug']}/"
    prod_node = {"@type": "Product", "@id": url + "#product", "name": p["name"], "description": p["short"],
                 "image": [og_url(main_key)] + [f"{DOMAIN}/assets/images/{variants(k)[-1][2]}" for k, _a in keys],
                 "brand": {"@type": "Brand", "name": BRAND}, "category": cat["name"], "url": url,
                 "manufacturer": {"@id": DOMAIN + "/#organization"}}
    bc = breadcrumb_node([("Home", "/"), ("Products", "/products/"), (cat["name"], f"/products/?category={cat['slug']}"), (p["name"], f"/products/{p['slug']}/")])
    org_min = {"@type": "Organization", "@id": DOMAIN + "/#organization", "name": COMPANY, "url": DOMAIN + "/"}
    desc = trunc(f'{p["short"]} Available for B2B, wholesale and distribution from Shreya Agro Foods, Mumbai.')
    page(f"products/{p['slug']}/index.html", title=f"{p['name']} | Shreya Agro Foods", desc=desc, body=body, active="products", og_key=main_key,
         schema=jsonld(prod_node, bc, org_min), body_attrs=f'data-product="{q(p["name"])}" data-category="{q(cat["name"])}"', sitemap_priority="0.7")


def build_vendor():
    hero = f"""<section class="vh"><div class="container vh-grid">
<div>
<span class="pill-eyebrow">B2B PARTNER</span>
<h1>Partner with <em>Shreya Agro Foods</em></h1>
<p class="vh-lead">Join hands with a trusted FMCG brand, delivering quality food products across India. We welcome distributors, wholesalers, retailers and business partners to grow together.</p>
<div class="hero-actions"><a class="btn btn-primary" href="#partner-form">Become a Partner {ARROW}</a><a class="btn btn-outline" href="/assets/images/brochure.pdf" download>Download Brochure {ic("download", "arrow")}</a></div>
</div>
<div class="vh-media">{img("hero-desktop", "Shreya Agro Foods products — jam, masala and soan papdi in front of the Shreya facility", sizes="(min-width:900px) 600px, 92vw", lazy=False, fetchpriority="high", cls="vh-img")}<span class="script vh-script">Quality Products<br>Greater Together</span></div>
</div></section>"""
    trust = ('<section class="trust-row" aria-label="Why partner with Shreya Agro Foods"><div class="container trust-grid">'
             + "".join(f'<div class="trust-item"><span class="round-icon">{ic(i)}</span><h3>{t}</h3><p>{d}</p></div>'
                       for i, t, d in [("shield-check", "Trusted Brand", "26+ years of experience"), ("truck", "Pan India Supply", "Wide distribution network"),
                                       ("award", "Consistent Quality", "From factory to your shelves"), ("users", "Long Term Partnership", "Grow together, succeed together"),
                                       ("headset", "Dedicated Support", "Always here for you")])
             + '</div></section>')
    minis = "".join(
        f'<a class="mini" href="/products/?category={c["slug"]}"><span class="mini-img">{img(c["img"], f"{BRAND} {c["name"]}", sizes="(min-width:1100px) 130px, (min-width:576px) 22vw, 44vw")}</span>'
        f'<b>{e(c["name"])}</b><span class="mini-link">Explore {ARROW}</span></a>' for c in CATEGORIES)
    rng = f"""<section class="section vp"><div class="container">
<div class="cat-head"><div><span class="pill-eyebrow">OUR PRODUCTS</span><h2>Wide Range of Quality Products</h2>
<p>From everyday essentials to traditional favourites, our diverse product range is crafted with care and delivered with trust.</p></div>
<a class="link-arrow" href="/products/">View All Products {ARROW}</a></div>
<div class="mini-grid">{minis}</div></div></section>"""
    why_items = "".join(
        f'<div class="why-item"><span class="round-icon sm">{ic(i)}</span><div><h3>{t}</h3><p>{d}</p></div></div>'
        for i, t, d in [("award", "Premium Quality Products", "High standards, always."), ("trend", "Competitive Pricing", "Better margins, higher growth."),
                        ("truck", "Reliable Supply Chain", "On-time, every time."), ("bulb", "Marketing Support", "Tools to help you sell more.")])
    form = f"""<section class="section why" id="partner-form"><div class="container two-col" style="align-items:start">
<div><span class="pill-eyebrow">WHY PARTNER WITH US</span><h2>Your Growth, Our Support</h2>
<p>We are committed to building strong and lasting relationships with our business partners. Here is why you should partner with us:</p>
<div class="why-items">{why_items}</div></div>
<div class="form-card">
<div id="partnerWrap"><h2 style="font-size:1.5rem">Become a B2B Partner</h2><p>Fill in your details and our team will get in touch with you shortly.</p>
<form id="partnerForm" data-form="partner" data-wrap="partnerWrap" data-success="partnerSuccess" data-subject="B2B partner enquiry — Shreya Agro Foods website" action="#">
<input type="hidden" name="enquiry_type" value="Business Partnership">
{HONEYPOT}
{field("Full Name", "name", required=True, placeholder="Full Name", fid="pt_name", autocomplete="name", icon="user")}
{field("Business Name", "company", required=True, placeholder="Business Name", fid="pt_company", autocomplete="organization", icon="building")}
{field("Email Address", "email", "email", required=True, placeholder="Email Address", fid="pt_email", autocomplete="email", icon="mail")}
{field("Phone Number", "mobile", "tel", required=True, placeholder="Phone Number", fid="pt_mobile", autocomplete="tel", icon="phone")}
{field("Location", "location", required=True, placeholder="City / State", fid="pt_location", autocomplete="address-level2", icon="pin")}
{select("Business Type", "business_type", ["Distributor", "Wholesaler", "Retailer", "Other"], required=True, fid="pt_type", placeholder="Select Business Type", icon="grid")}
{textarea("Message (optional)", "message", placeholder="Message (Optional)", fid="pt_message", icon="chat")}
<p class="form-status" role="alert" hidden></p>
{submit_btn("Submit Enquiry")}
<p class="form-note" style="display:flex;gap:6px;justify-content:center;align-items:center">{ic("shield-check", "note-icon")} Your information is safe with us.</p>
</form></div>
{success_box("partnerSuccess", text="Your enquiry has been received successfully. Our B2B team will contact you within 24 hours.")}
</div></div></section>"""
    steps_data = [("file", "Submit Enquiry", "Tell us about your business needs."), ("phone", "Our Team Connects", "We will get in touch with you within 24 hours."),
                  ("users", "Agreement & Onboarding", "Complete the process and start your journey with us."), ("trend", "Grow Together", "Begin supply and grow together with our support.")]
    step_html = ""
    for i, (ico, t, d) in enumerate(steps_data):
        step_html += f'<div class="step2"><span class="num">{i + 1}</span><span class="step2-icon">{ic(ico if ico != "file" else "package")}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></div>'
        if i < len(steps_data) - 1:
            step_html += f'<span class="step2-arrow" aria-hidden="true">{ic("arrow")}</span>'
    steps = (f'<section class="section steps2-sec"><div class="container"><span class="pill-eyebrow">HOW IT WORKS</span><h2>Simple Steps to Partner</h2>'
             f'<div class="steps2">{step_html}</div></div></section>')
    strip = f"""<section class="cta-strip"><div class="container cta-strip-grid">
<div class="cta-brand"><img src="/assets/images/shreya-agro-foods-logo-160.webp" alt="" width="160" height="116" loading="lazy" decoding="async"><div><strong>Shreya Agro Foods</strong><span>Quality Food &nbsp;|&nbsp; Trusted Partner &nbsp;|&nbsp; Growing Together</span></div></div>
<div class="cta-text"><h2>Let's Build Something Great Together</h2><p>Partner with Shreya Agro Foods and bring quality food products to more homes across India.</p></div>
<button type="button" class="btn btn-light" data-enquiry data-type="Business Partnership">Become a B2B Partner {ARROW}</button>
</div></section>"""
    page("vendor/index.html", title="Become a B2B Partner | Shreya Agro Foods",
         desc="Partner with Shreya Agro Foods as a distributor, wholesaler or retailer. Explore our FMCG range and send a B2B partnership enquiry.",
         body=hero + trust + rng + form + steps + strip, active="vendor", og_key="hero-desktop", sitemap_priority="0.8",
         schema=jsonld(ORG_NODE, breadcrumb_node([("Home", "/"), ("Vendor", "/vendor/")])))


def build_contact():
    hero = f"""<section class="page-hero has-image center" style="--hero-img:url(/assets/images/shreya-agro-foods-hero-desktop-1200.webp)"><div class="container">
<span class="eyebrow">Contact &amp; Careers</span>
<h1>Let's Connect</h1>
<p class="lead">Whether you're looking for a business partnership, product enquiry, distribution opportunity or a career with us, we'd love to hear from you.</p>
<div class="hero-actions"><button type="button" class="btn btn-accent" data-enquiry data-type="B2B Enquiry">Make a B2B Enquiry {ARROW}</button><a class="btn btn-outline-light" href="#careers">View Careers</a></div>
</div></section>"""
    info = f"""<div>
<span class="eyebrow">Contact</span><h2>Get in Touch</h2>
<p>Our team is ready to answer your questions. Fill out the form or reach us directly by phone or email.</p>
<div class="info-card"><div class="icon">{ic("pin")}</div><div><h3>Our Office</h3><p>{ADDRESS}</p></div></div>
<div class="info-card"><div class="icon">{ic("phone")}</div><div><h3>Phone</h3><p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p></div></div>
<div class="info-card"><div class="icon">{ic("mail")}</div><div><h3>Email</h3><p><a href="mailto:{EMAIL}">{EMAIL}</a></p></div></div>
<div class="info-card"><div class="icon">{ic("briefcase")}</div><div><h3>Business Enquiries</h3><p>For products, distribution and partnerships.</p></div></div>
<div class="info-card"><div class="icon">{ic("clock")}</div><div><h3>Business Hours</h3><p>Mon–Fri 10am–6pm · Sat 10am–2pm</p></div></div>
</div>"""
    form = f"""<div class="form-card">
<div id="contactWrap"><h2 style="font-size:1.6rem">Send Us an Enquiry</h2><p>Fill out the form below and we'll get back to you within 24 hours.</p>
<form id="contactForm" data-form="contact" data-wrap="contactWrap" data-success="contactSuccess" data-subject="Website enquiry — Shreya Agro Foods" action="#">
{HONEYPOT}
{field("Name", "name", required=True, placeholder="Enter your name", fid="g_name", autocomplete="name")}
{field("Company Name", "company", placeholder="Enter company name", fid="g_company", autocomplete="organization")}
<div class="field-row">{field("Mobile Number", "mobile", "tel", required=True, placeholder="Enter mobile number", fid="g_mobile", autocomplete="tel")}{field("Email", "email", "email", placeholder="Enter email address", fid="g_email", autocomplete="email")}</div>
<div class="field-row">{field("Location", "location", required=True, placeholder="City / State", fid="g_location", autocomplete="address-level2")}{select("Enquiry Type", "enquiry_type", ENQUIRY_TYPES, required=True, fid="g_type", placeholder="Select enquiry type")}</div>
{textarea("Message", "message", placeholder="Tell us how we can help you...", fid="g_message", rows=4)}
<p class="form-status" role="alert" hidden></p>
{submit_btn("Submit Enquiry")}
</form></div>
{success_box("contactSuccess", text="Your enquiry has been received successfully. Our team will get back to you shortly.")}
</div>"""
    contact = f'<section class="section"><div class="container contact-grid">{info}{form}</div></section>'
    banner = cta_band("Looking for a Long-Term FMCG Partner?", "Connect with Shreya Agro Foods for B2B, wholesale, distribution and business opportunities.",
                      primary_label="Become a B2B Partner", secondary=("View Our Products", "/products/"), full=True).replace(
        'data-enquiry data-type="B2B Enquiry"', 'data-enquiry data-type="Business Partnership"')
    why = feature_cards([("sprout", "Growth", "Opportunities to learn, develop and grow."), ("users", "Collaboration", "Work with a team that values ideas and teamwork."),
                         ("bulb", "Innovation", "Be part of a company continuously evolving with the market."), ("trend", "Opportunity", "Build your career in a growing FMCG environment.")])
    if JOBS:
        jobs_html = "".join(f"""<article class="job"><div class="job-top"><div><h3>{e(j["title"])}</h3>
<div class="job-meta"><span>{ic("pin")}{e(j["location"])}</span><span>{ic("briefcase")}{e(j["type"])}</span></div></div>
<div class="job-buttons"><button type="button" class="btn btn-primary btn-sm" data-apply="{q(j["title"])}">Apply Now {ARROW}</button></div></div>
<details class="job-details-wrap" style="margin-top:12px"><summary style="cursor:pointer;font-weight:700;color:var(--primary)">View Details</summary><div class="job-details"><p>{e(j["summary"])}</p><ul>{"".join(f"<li>{e(d)}</li>" for d in j["details"])}</ul></div></details></article>""" for j in JOBS)
        openings = f'<div class="job-list">{jobs_html}</div>'
    else:
        openings = f"""<div class="empty-jobs"><h3>No Current Openings</h3><p>We don't have any active positions at the moment, but we're always interested in meeting talented people.</p>
<button type="button" class="btn btn-primary" data-apply="General Application">Send Your Resume {ARROW}</button></div>"""
    careers = f"""<section class="section section-tint" id="careers"><div class="container">
{section_head("Careers", "Build Your Career With Shreya Agro Foods", "We are always looking for passionate, talented and motivated people who want to grow with a growing FMCG organization. Explore opportunities. Grow with us. Make an impact.", center=True)}
<h3 style="text-align:center;margin:0 0 24px;font-size:1.4rem">Why Work With Us?</h3>
{why}
</div></section>
<section class="section" id="openings"><div class="container">
{section_head("Current Openings", "Current Openings", center=True)}
{openings}
</div></section>"""
    find = f"""<section class="section section-alt"><div class="container">
{section_head("Find Us", "Find Us", f"{COMPANY}, Mumbai, Maharashtra", center=True)}
<div class="map-wrap"><iframe title="Map showing {COMPANY} in Goregaon East, Mumbai" src="{MAP_SRC}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
</div></section>"""
    lb = {"@type": ["LocalBusiness"], "@id": DOMAIN + "/#localbusiness", "name": COMPANY, "url": DOMAIN + "/", "telephone": "+91-70586-74452", "email": EMAIL,
          "image": DOMAIN + "/assets/images/og/shreya-agro-foods-hero-desktop.jpg", "address": ORG_NODE["address"],
          "openingHoursSpecification": [
              {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "10:00", "closes": "18:00"},
              {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "14:00"}]}
    page("contact-us/index.html", title="Contact Shreya Agro Foods | B2B & Business Enquiries",
         desc="Contact Shreya Agro Foods in Mumbai for B2B enquiries, distribution, partnerships and careers. Call, email or send an enquiry online.",
         body=hero + contact + banner + careers + find, active="contact", extra_modals=apply_modal(), og_key="hero-desktop", sitemap_priority="0.8",
         schema=jsonld(ORG_NODE, lb, breadcrumb_node([("Home", "/"), ("Contact Us", "/contact-us/")])))


def build_careers_redirect():
    # /careers/ is a short, memorable URL; the careers content lives on the combined Contact & Careers page.
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Careers at Shreya Agro Foods | Job Opportunities</title>
<meta name="description" content="Careers at Shreya Agro Foods — see current openings and apply online.">
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{DOMAIN}/contact-us/#careers">
<meta http-equiv="refresh" content="0; url=/contact-us/#careers">
<script>location.replace("/contact-us/#careers");</script>
</head>
<body><p>Careers are listed on our <a href="/contact-us/#careers">Contact &amp; Careers page</a>.</p></body>
</html>
"""
    write("careers/index.html", doc)


def build_404():
    body = f"""<section class="error-page"><div class="container">
<div class="code" aria-hidden="true">404</div>
<h1 style="font-size:clamp(1.8rem,4vw,2.6rem)">Page Not Found</h1>
<p>The page you're looking for may have moved or no longer exists.</p>
<div class="hero-actions"><a class="btn btn-primary" href="/">Go Home {ARROW}</a><a class="btn btn-outline" href="/products/">Explore Products</a><a class="btn btn-outline" href="/contact-us/">Contact Us</a></div>
</div></section>"""
    page("404.html", title="Page Not Found | Shreya Agro Foods", desc="The page you're looking for may have moved or no longer exists.", body=body, noindex=True, og_key="hero-desktop")


def build_seo_files():
    urls = "".join(f"  <url>\n    <loc>{DOMAIN}{u}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n    <priority>{pr}</priority>\n  </url>\n" for u, pr in PAGES)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    write(".htaccess", HTACCESS)


HTACCESS = """# Shreya Agro Foods — Apache config (Hostinger / cPanel)
Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
RewriteEngine On

# One canonical host: HTTPS + www (matches the canonical URLs in every page)
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} ^shreyaagrofoods\\.com$ [NC]
RewriteRule ^ https://www.shreyaagrofoods.com%{REQUEST_URI} [L,R=301]

# Old URL from the previous build
RewriteRule ^vendor\\.html$ /vendor/ [L,R=301]
</IfModule>

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript text/javascript application/json application/ld+json image/svg+xml application/xml
</IfModule>

<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/webp "access plus 1 year"
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType image/png "access plus 1 year"
ExpiresByType font/woff2 "access plus 1 year"
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"
ExpiresByType text/javascript "access plus 1 year"
ExpiresByType text/html "access plus 0 seconds"
</IfModule>

<IfModule mod_headers.c>
Header set X-Content-Type-Options "nosniff"
Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>
"""


def main():
    global ASSET_V
    ASSET_V = build_assets()
    build_home()
    build_about()
    build_products()
    for p in PRODUCTS:
        build_product(p)
    build_vendor()
    build_contact()
    build_careers_redirect()
    build_404()
    build_seo_files()
    print(f"built {len(PAGES)} indexable pages (assets v={ASSET_V})")


if __name__ == "__main__":
    main()
