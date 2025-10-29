import time
import re
from datetime import datetime
import pandas as pd
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===================== CONFIG =====================
OUTPUT_CSV = "snapdeal_products.csv"
HEADLESS = True
SCROLL_PAUSE = 0.8
LISTING_WAIT = 10
MAX_PAGES_PER_SUBCAT = 3
DEEP_SCRAPE = False          # Set True for full details
MAX_PRODUCTS_PER_SUBCAT: Optional[int] = None

BASE_SECTIONS = {
    "Accessories":     "https://www.snapdeal.com/search?keyword=accessories&sort=rlvncy",
    "Footwear":        "https://www.snapdeal.com/search?keyword=footwear&sort=rlvncy",
    "Kids' Fashion":   "https://www.snapdeal.com/search?keyword=kids%20fashion&sort=rlvncy",
    "Men's Clothing":  "https://www.snapdeal.com/search?keyword=men%20clothing&sort=rlvncy",
    "Women's Clothing":"https://www.snapdeal.com/search?keyword=women%20clothing&sort=rlvncy",
}
# ==================================================

# ---------- Selenium setup ----------
chrome_opts = Options()
if HEADLESS:
    chrome_opts.add_argument("--headless=new")
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--window-size=1920,1080")
chrome_opts.add_argument("--no-sandbox")
chrome_opts.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_opts
)
wait = WebDriverWait(driver, LISTING_WAIT)

# ---------- Helper Functions ----------

def human_sleep(sec: float) -> None:
    time.sleep(sec)

def scroll_to_bottom(max_scrolls: int = 20) -> None:
    """Scroll gradually down."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def clean_int(text: Optional[str]) -> int:
    """Safely extract integer from string."""
    if not text:
        return 0
    try:
        nums = re.findall(r"\d+", str(text))
        return int(nums[0]) if nums else 0
    except Exception:
        return 0

def parse_rating_from_style(style: Optional[str]) -> str:
    """Convert percentage style width to rating."""
    if not style:
        return ""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", style)
    return f"{round(float(m.group(1)) / 20, 1)}" if m else ""

def safe_text(el) -> str:
    try:
        return el.text.strip()
    except Exception:
        return ""

def find_first(selectors, in_el=None, attr=None, by=By.CSS_SELECTOR) -> str:
    ctx = in_el if in_el is not None else driver
    for sel in selectors:
        try:
            el = ctx.find_element(by, sel)
            return el.get_attribute(attr).strip() if attr else el.text.strip()
        except Exception:
            continue
    return ""

def find_all(selector, in_el=None, by=By.CSS_SELECTOR):
    ctx = in_el if in_el is not None else driver
    try:
        return ctx.find_elements(by, selector)
    except Exception:
        return []

def click_next_page() -> bool:
    """Go to next page safely."""
    try:
        curr_url = driver.current_url
    except Exception:
        return False

    selectors = [
        "a[rel='next']",
        "a.pagination-number.next",
        "a.next",
        "//a[contains(translate(., 'NEXT', 'next'),'next')]",
    ]
    for sel in selectors:
        try:
            elem = driver.find_element(By.XPATH, sel) if sel.startswith("//") else driver.find_element(By.CSS_SELECTOR, sel)
            driver.execute_script("arguments[0].click();", elem)
            human_sleep(1.2)
            WebDriverWait(driver, 6).until(EC.url_changes(curr_url))
            if driver.current_url != curr_url:
                return True
        except Exception:
            continue
    return False

def deep_scrape_product(url: str) -> dict:
    """Scrape detailed info from product page."""
    data = {
        "Brand": "", "Full Description": "", "Seller": "",
        "Availability": "", "Rating": "", "Reviews Count": 0,
        "Breadcrumb": "", "Image URLs (detail)": ""
    }
    if not url:
        return data

    current_page = driver.current_url
    try:
        driver.get(url)
        data["Brand"] = find_first(["span[itemprop='brand']", "a#brand", ".pdp-e-i-brand a"])
        rating_val = find_first(["span[itemprop='ratingValue']", ".pdp-e-i-rating"])
        if not rating_val:
            style = find_first([".filled-stars"], attr="style")
            rating_val = parse_rating_from_style(style)
        data["Rating"] = rating_val
        data["Reviews Count"] = clean_int(find_first(["span[itemprop='reviewCount']", ".pdp-review-count"]))
        data["Availability"] = find_first([".sold-out-err", ".availability-msg"]) or "In Stock"
        data["Seller"] = find_first(["#sellerName", ".pdp-seller-info a"])
        data["Full Description"] = find_first(["#description", ".product-desc"])
        crumbs = find_all("ul.breadcrumb li")
        if crumbs:
            data["Breadcrumb"] = " > ".join([safe_text(li) for li in crumbs if safe_text(li)])
        imgs = [img.get_attribute("src") for img in find_all("img") if (img.get_attribute("src") or "").startswith("http")]
        data["Image URLs (detail)"] = ", ".join(dict.fromkeys(imgs))[:2000]
    except Exception as e:
        print(f"[deep_scrape_product] error: {e}")
    finally:
        driver.get(current_page)
    return data

# ===================== MAIN =====================
all_rows = []

try:
    for section_name, base_url in BASE_SECTIONS.items():
        print(f"\n=== Section: {section_name} ===")
        driver.get(base_url)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tuple-listing")))
        except Exception:
            pass

        subcats = [{"Subcategory": "(All)", "URL": base_url}]

        for sc in subcats:
            sub_name, sub_url = sc["Subcategory"], sc["URL"]
            print(f"\n→ Subcategory: {sub_name}")
            driver.get(sub_url)
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-tuple-listing")))
            except Exception:
                pass

            total_this_sub = 0
            for page in range(1, MAX_PAGES_PER_SUBCAT + 1):
                print(f"   • Page {page}")
                scroll_to_bottom()
                cards = find_all("div.product-tuple-listing") or find_all("div.product-tuple")
                if not cards:
                    break

                for card in cards:
                    name = find_first(["p.product-title"], in_el=card)
                    price_text = find_first(["span.product-price"], in_el=card)
                    price = clean_int(price_text)
                    url = find_first(["a.dp-widget-link"], in_el=card, attr="href")
                    extra = deep_scrape_product(url) if DEEP_SCRAPE and url else {}

                    row = {
                        "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Top Section": section_name,
                        "Subcategory": sub_name,
                        "Product Name": name,
                        "Price": int(price) if price is not None else 0,
                        "Product URL": url,
                        "Brand": extra.get("Brand", ""),
                        "Rating": extra.get("Rating", ""),
                        "Reviews Count": int(extra.get("Reviews Count", 0)),
                        "Seller": extra.get("Seller", ""),
                        "Availability": extra.get("Availability", ""),
                        "Full Description": extra.get("Full Description", ""),
                        "Breadcrumb": extra.get("Breadcrumb", ""),
                        "Image URLs (detail)": extra.get("Image URLs (detail)", ""),
                        "Page": int(page)
                    }

                    all_rows.append(row)
                    total_this_sub += 1
                    if MAX_PRODUCTS_PER_SUBCAT and total_this_sub >= MAX_PRODUCTS_PER_SUBCAT:
                        break

                moved = click_next_page()
                if not moved:
                    break

            print(f"   Collected {total_this_sub} products from '{sub_name}'")

finally:
    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✔ Done. Rows: {len(df)} → {OUTPUT_CSV}")
    driver.quit()