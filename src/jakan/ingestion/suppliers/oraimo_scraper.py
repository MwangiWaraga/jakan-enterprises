from __future__ import annotations
import logging, os, random, re, time
from typing import Optional
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from jakan.common.config import get_env_float
from jakan.common.text import parse_money, make_source_product_key
from jakan.common.ids import new_run_id, utc_now
from jakan.common.db import insert_rows

BASE_URL = os.getenv("ORAIMO_BASE_URL", "https://ke.oraimo.com")
CATEGORY_SLUGS = ["audio", "power", "smart-office", "personal-care", "home-appliances", "oraimo-home", "oraimo-baby"]
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
REQUEST_DELAY_RANGE = (get_env_float("REQUEST_DELAY_MIN_SECONDS", 1.0), get_env_float("REQUEST_DELAY_MAX_SECONDS", 1.8))
MAX_PAGES_PER_COLLECTION = int(os.getenv("MAX_PAGES_PER_COLLECTION", "60"))
CURRENCY = "KES"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JakanDataStack/1.0; +local-mvp) PythonRequests",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-KE,en;q=0.8",
    "Connection": "close",
}

def sleep_politely():
    time.sleep(random.uniform(*REQUEST_DELAY_RANGE))

def absolute_url(href: str | None) -> str:
    return "" if not href else urljoin(BASE_URL, href)

def extract_slug(product_url: str) -> str:
    try:
        path = urlparse(product_url).path
        if "/product/" in path:
            return path.split("/product/", 1)[1].strip("/").split("/")[0]
        return path.strip("/")
    except Exception:
        return ""

def extract_ean_from_url(href: str) -> Optional[str]:
    try:
        ean = parse_qs(urlparse(href).query).get("ean", [])
        return ean[0] if ean else None
    except Exception:
        return None

def first_text(root, selectors: list[str]) -> str:
    for sel in selectors:
        el = root.select_one(sel)
        if el:
            txt = el.get_text(strip=True)
            if txt:
                return txt
    return ""

def fetch(url: str) -> Optional[str]:
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                return resp.text
            if 400 <= resp.status_code < 500:
                return None
        except requests.RequestException as ex:
            logging.warning("Request error attempt %s for %s: %s", attempt, url, ex)
        sleep_politely()
    return None

def parse_tile(div) -> Optional[dict]:
    a = div.select_one('a[href^="/product/"]')
    if not a:
        return None

    href = a.get("href", "").strip()
    product_url = absolute_url(href)
    slug = extract_slug(product_url)
    title = a.get("data-name") or a.get_text(strip=True)
    model = (a.get("data-sku") or "").strip()
    ean = extract_ean_from_url(href) or ""

    img = div.select_one(".product-picture-wrap img")
    main_img = ""
    if img:
        main_img = img.get("src") or img.get("data-src") or ""
        if not main_img and img.get("srcset"):
            main_img = img.get("srcset").split(",")[0].split()[0]
        main_img = absolute_url(main_img)

    short_points = []
    for pp in div.select("div.product-points p.product-point"):
        spans = pp.find_all("span")
        if spans:
            txt = spans[-1].get_text(strip=True)
            if txt:
                short_points.append(txt)

    price_now_txt = first_text(div, [".product-desc .product-price span", "p.product-price span", ".product-price span"])
    price_was_txt = first_text(div, [".product-desc .product-price del", "p.product-price del", ".product-price del"])

    if not price_now_txt:
        price_now_txt = a.get("data-price") or ""
        if not price_now_txt:
            btn = div.select_one("a.js_add_to_cart")
            if btn:
                price_now_txt = btn.get("data-price") or ""

    tile_text = div.get_text(" ", strip=True).lower()
    if "out of stock" in tile_text:
        stock_status = "OutOfStock"
    elif div.select_one("a.js_add_to_cart"):
        stock_status = "InStock"
    else:
        stock_status = "Unknown"

    return {
        "source_system": "ORAIMO",
        "source_product_key": make_source_product_key(ean, model, slug, product_url),
        "product_url": product_url,
        "title": title,
        "short_description": ", ".join(short_points),
        "price_now_raw": price_now_txt or "",
        "price_now_num": parse_money(price_now_txt),
        "price_was_raw": price_was_txt or "",
        "price_was_num": parse_money(price_was_txt),
        "currency": CURRENCY,
        "main_image_url": main_img,
        "ean": ean,
        "model": model,
        "stock_status": stock_status,
        "slug": slug,
    }

def parse_collection(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    return [item for div in soup.select("div.js_product.site-product") if (item := parse_tile(div))]

def get_total_pages(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    match = re.search(r"Total\s+(\d+)\s+Pages", soup.get_text(), re.IGNORECASE)
    if match:
        return int(match.group(1))
    nums = []
    for link in soup.find_all("a", href=re.compile(r"page=\d+")):
        m = re.search(r"page=(\d+)", link.get("href", ""))
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 1

def scrape_category(slug: str) -> list[dict]:
    all_items, seen_urls, total_pages = [], set(), MAX_PAGES_PER_COLLECTION
    for page in range(1, MAX_PAGES_PER_COLLECTION + 1):
        if page > total_pages:
            break
        url = f"{BASE_URL}/collections/{slug}?page={page}"
        logging.info("Fetching %s", url)
        html = fetch(url)
        if not html:
            break
        if page == 1:
            total_pages = min(get_total_pages(html), MAX_PAGES_PER_COLLECTION)
        items = parse_collection(html)
        if not items:
            break
        new_items = [x for x in items if x["product_url"] not in seen_urls]
        for item in new_items:
            item["category"] = slug.replace("-", " ").title()
        all_items.extend(new_items)
        seen_urls.update(x["product_url"] for x in new_items)
        sleep_politely()
        if page > 1 and len(new_items) == 0:
            break
    return all_items

def scrape_all_categories() -> list[dict]:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    all_rows = []
    for slug in CATEGORY_SLUGS:
        rows = scrape_category(slug)
        logging.info("%s: %s items", slug, len(rows))
        all_rows.extend(rows)
    return all_rows

def load_oraimo_to_postgres(rows: list[dict]) -> int:
    run_id, scraped_at = new_run_id("oraimo"), utc_now()
    db_rows = []
    for row in rows:
        db_rows.append({
            "scrape_run_id": run_id,
            "scraped_at": scraped_at,
            "source_system": row.get("source_system", "ORAIMO"),
            "source_product_key": row.get("source_product_key", ""),
            "category": row.get("category", ""),
            "product_url": row.get("product_url", ""),
            "title": row.get("title", ""),
            "short_description": row.get("short_description", ""),
            "price_now_raw": row.get("price_now_raw", ""),
            "price_now_num": row.get("price_now_num"),
            "price_was_raw": row.get("price_was_raw", ""),
            "price_was_num": row.get("price_was_num"),
            "currency": row.get("currency", CURRENCY),
            "main_image_url": row.get("main_image_url", ""),
            "ean": row.get("ean", ""),
            "model": row.get("model", ""),
            "stock_status": row.get("stock_status", ""),
            "slug": row.get("slug", ""),
            "raw_payload": row,
        })
    return insert_rows("raw.oraimo_products", db_rows)
