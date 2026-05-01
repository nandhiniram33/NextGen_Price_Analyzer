from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pandas as pd
from functools import lru_cache
import time
import threading
import json
import re
import pickle
from typing import Dict, Any

# disk cache location for product clusters
CACHE_DIR = os.path.dirname(__file__)
PRODUCTS_CACHE_FILE = os.path.join(CACHE_DIR, 'product_clusters.pkl')


def normalize_name_for_exact(s: str) -> str:
    """Normalize a product name for exact search comparisons.

    Removes parenthetical content, replaces non-alphanumeric characters with
    spaces, lowercases and strips.
    """
    if not isinstance(s, str):
        return ""
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^0-9a-zA-Z]+", " ", s).lower().strip()
    return s

app = Flask(__name__, template_folder="templates")
# Simple secret for session handling (development/demo only)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")

# User storage file
USERS_FILE = os.path.join(os.getcwd(), "users.json")

# Load users from file
def load_users():
    """Load registered users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

# Save users to file
def save_users(users):
    """Save registered users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception:
        pass

# Load users at startup
registered_users = load_users()

# Global cache variables
_cached_data = None
_cached_products = None
_cache_time = None
_enriched_map_cache = None  # store enriched map once
_products_norm = None  # normalized product names parallel to _cached_products
_users_meta = None

# Electronics brands and categories whitelist
ELECTRONIC_CATEGORIES = set([
    "smartphones", "smartwatch", "headphones", "television", "laptop", 
    "tablet", "camera", "speaker", "gaming console", "drone"
])

ELECTRONICS_BRANDS = set([
    # Smartphones
    "apple", "samsung", "xiaomi", "realme", "oneplus", "oppo", "vivo", "motorola",
    "poco", "infinix", "tecno", "honor", "nokia", "lg", "sony", "itel", "asus", "lenovo",
    # Smartwatch
    "noise", "boat", "fastrack", "garmin",
    # Headphones
    "jbl", "bose", "beats", "sennheiser", "audio-technica",
    # TV
    "tcl", "panasonic", "hisense", "bpl", "kodak",
    # Laptop
    "dell", "hp", "acer", "msi",
    # Tablet
    "microsoft",
    # Camera
    "canon", "nikon", "fujifilm", "gopro",
    # Speaker
    "ultimate ears",
    # Gaming
    # Drone
    "dji", "parrot"
])


def load_all_data():
    """Load all CSV data with caching"""
    global _cached_data, _cache_time
    
    # Return cached data if available
    if _cached_data is not None:
        return _cached_data
    
    print("🔄 Loading datasets (first time only)...")
    start = time.time()
    
    # Discover CSVs in the project `dataset/` folder (provided files).
    import glob
    data_dir = os.path.join(os.getcwd(), "dataset")
    pattern = os.path.join(data_dir, "*.csv")
    files = glob.glob(pattern)

    existing = [f for f in files if os.path.exists(f)]
    if not existing:
        return pd.DataFrame(
            columns=[
                "product_name",
                "image_url",
                "brand",
                "website",
                "price",
                "rating",
                "warranty_years",
                "product_link",
            ]
        )

    # Read all CSVs and normalize columns to a common schema
    dfs = []
    for file in existing:
        try:
            d = pd.read_csv(file, dtype={'price': 'float64', 'rating': 'float64', 'warranty_years': 'int64'})
        except Exception:
            continue

        # If file uses separate brand+model, combine into product_name
        if "product_name" not in d.columns:
            if "brand" in d.columns and "model" in d.columns:
                def clean_product_name(row):
                    brand = str(row.get("brand", "")).strip().lower()
                    model = str(row.get("model", "")).strip()
                    brand_cap = brand.capitalize()
                    if model.lower().startswith(brand + " "):
                        model_clean = model[len(brand) + 1:]
                    else:
                        model_clean = model
                    return brand_cap + " " + model_clean
                d["product_name"] = d.apply(clean_product_name, axis=1)
            elif "model" in d.columns:
                d["product_name"] = d["model"].astype(str).str.strip()
            else:
                d["product_name"] = d.iloc[:, 0].astype(str).astype(str)

        # Ensure website column exists
        if "website" not in d.columns:
            # try to infer from filename
            name = os.path.basename(file).lower()
            w = ""
            for site in ["amazon", "flipkart", "meesho", "myntra", "snapdeal", "reliancedigital", "croma"]:
                if site in name:
                    w = site.capitalize() if site != "reliancedigital" else "RelianceDigital"
                    break
            d["website"] = w

        # Add placeholder image if missing
        if "image_url" not in d.columns:
            d["image_url"] = "static/placeholder.svg"

        # Add product_link if missing but product_id present
        if "product_link" not in d.columns:
            if "product_id" in d.columns:
                # form a simple product link based on website and id
                def make_link(row):
                    try:
                        site = str(row.get("website", "")).lower()
                        pid = str(row.get("product_id", "")).strip()
                        if not pid:
                            return ""
                        base = f"https://{site}.com/" if site else ""
                        return base + pid
                    except Exception:
                        return ""
                d["product_link"] = d.apply(make_link, axis=1)
            else:
                d["product_link"] = ""

        # Ensure price and rating exist
        if "price" not in d.columns:
            d["price"] = ""
        if "rating" not in d.columns:
            d["rating"] = ""

        # Ensure warranty_years column exists
        if "warranty_years" not in d.columns:
            d["warranty_years"] = ""

        # Keep only needed columns and also preserve common spec columns if present
        spec_cols = ["model", "category", "display", "processor", "ram", "storage", "camera", "battery", "product_id"]
        base_cols = ["product_name", "image_url", "brand", "website", "price", "rating", "warranty_years", "product_link"]
        keep_cols = [c for c in (base_cols + spec_cols) if c in d.columns]
        dfs.append(d[keep_cols].copy())

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True, sort=False)

    # Normalize website values to consistent casing (e.g., 'Flipkart')
    if "website" in df.columns:
        df["website"] = df["website"].astype(str).str.strip()

    # Normalize price to numeric where possible
    try:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    except Exception:
        pass

    # Cache the data
    _cached_data = df.reset_index(drop=True)
    _cache_time = time.time()
    elapsed = _cache_time - start
    print(f"✓ Datasets loaded in {elapsed:.2f}s ({len(_cached_data)} products cached)")
    
    return _cached_data


def _load_enriched_map():
    """Load dataset/enriched_products.json into a dict keyed by product||website.
    Cache result so subsequent calls are fast.
    """
    global _enriched_map_cache
    if _enriched_map_cache is not None:
        return _enriched_map_cache

    enriched_path = os.path.join(os.getcwd(), "dataset", "enriched_products.json")
    m = {}
    try:
        if os.path.exists(enriched_path):
            with open(enriched_path, "r", encoding="utf-8") as f:
                items = json.load(f)
                for e in items:
                    key = f"{e.get('product_name','')}||{e.get('website','')}"
                    m[key] = e
    except Exception as ex:
        print(f"Error loading enriched map: {ex}")
    _enriched_map_cache = m
    return m


def _load_users_meta():
    """Load or initialize users_meta.json (separate from users.json)."""
    global _users_meta
    if _users_meta is not None:
        return _users_meta
    path = os.path.join(os.getcwd(), "users_meta.json")
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _users_meta = json.load(f)
                return _users_meta
    except Exception:
        pass
    _users_meta = {}
    return _users_meta


def _save_users_meta(meta: Dict[str, Any]):
    try:
        path = os.path.join(os.getcwd(), "users_meta.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_all_products():
    """Get all products with caching and optional disk persistence."""
    global _cached_products, _products_norm

    # memory cache
    if _cached_products is not None:
        return _cached_products

    # try loading from disk cache file
    if os.path.exists(PRODUCTS_CACHE_FILE):
        try:
            with open(PRODUCTS_CACHE_FILE, 'rb') as f:
                _cached_products, _products_norm = pickle.load(f)
                print(f"✓ Loaded {len(_cached_products)} product clusters from cache file")
                return _cached_products
        except Exception as ex:
            print(f"Failed to read cache file: {ex}")

    # build clusters from raw data
    print("🔄 Building product clusters (first time only)...")
    start = time.time()

    data = load_all_data()
    _cached_products = build_products_list(data)
    # precompute normalized names for search
    _products_norm = [normalize_name_for_exact(p.get('product_name', '')) for p in _cached_products]

    elapsed = time.time() - start
    print(f"✓ Product clusters built in {elapsed:.2f}s ({len(_cached_products)} clusters cached)")

    # persist to disk for future restarts
    try:
        with open(PRODUCTS_CACHE_FILE, 'wb') as f:
            pickle.dump((_cached_products, _products_norm), f)
            print(f"✓ Wrote product clusters to disk cache")
    except Exception as ex:
        print(f"Failed to write cache file: {ex}")

    return _cached_products


# Warm the product cache asynchronously to avoid slow first-request latency
def _warm_cache_background():
    try:
        get_all_products()
    except Exception:
        pass

# Start background warm-up thread (daemon so it won't block shutdown)
threading.Thread(target=_warm_cache_background, daemon=True).start()


def build_products_list(df):
    """
    Cluster products across websites by token-set similarity so each product
    contains entries from all sites. Returns list of product dicts with an
    additional `tokens` set for search filtering.
    """
    import re

    def normalize_name(name: str):
        if not isinstance(name, str):
            return ""
        # remove parentheses content
        name = re.sub(r"\(.*?\)", "", name)
        # replace non-alphanum with spaces
        name = re.sub(r"[^0-9a-zA-Z]+", " ", name)
        name = name.lower().strip()
        tokens = [t for t in name.split() if t]
        # filter out common tokens that add noise
        stop = set(["inch", "gb", "g", "ram", "storage", "ch", "blue", "black", "white",
                    "red", "green", "blue", "gold", "silver", "mm"])
        tokens = [t for t in tokens if t not in stop and not t.isdigit()]
        return tokens

    def jaccard(a, b):
        if not a or not b:
            return 0.0
        ia = set(a)
        ib = set(b)
        inter = ia.intersection(ib)
        union = ia.union(ib)
        return len(inter) / len(union)

    products = []
    if df is None or df.empty:
        return products

    rows = df.copy()
    rows["_name"] = rows["product_name"].astype(str).str.strip()
    rows["_tokens"] = rows["_name"].apply(normalize_name)

    # Group products by a normalized token string for much faster clustering.
    # This trades some fuzzy merging for a large speed-up on big datasets.
    rows["_norm_str"] = rows["_tokens"].apply(lambda toks: " ".join(toks) if toks else "")
    grouped = rows.groupby("_norm_str")

    # Build product dicts
    for key, group_rows in grouped:
        # `group_rows` is a DataFrame slice for this normalized token signature


        image_url = ""
        if "image_url" in group_rows.columns:
            non_null = group_rows["image_url"].dropna().tolist()
            # Use first non-empty image_url
            non_empty = [img for img in non_null if img and str(img).strip() and img != "static/placeholder.svg" and img != "" and img != "/static/placeholder.png"]
            if non_empty:
                image_url = str(non_empty[0]).strip()
            elif non_null:
                image_url = str(non_null[0]).strip()

        brand = ""
        if "brand" in group_rows.columns and not group_rows["brand"].dropna().empty:
            brand = group_rows["brand"].dropna().iloc[0]
        
        # Extract actual brand from product_name if brand is "Various"
        if brand and brand.lower() == "various":
            # Try to extract brand from product_name (first word or model column)
            rep_name = group_rows["product_name"].iloc[0]
            
            # First, check if there's a model that might be the brand
            if "model" in group_rows.columns and not group_rows["model"].dropna().empty:
                model = str(group_rows["model"].dropna().iloc[0]).strip()
                # If model starts with a capital word, use it as brand
                if model and len(model.split()) > 0:
                    potential_brand = model.split()[0]
                    if potential_brand and not potential_brand.isdigit():
                        brand = potential_brand
            
            # If still "Various", try parsing from product_name
            if brand.lower() == "various":
                # Remove "Various" prefix if present
                clean_name = rep_name.replace("Various", "").strip()
                # Get first meaningful word
                parts = clean_name.split()
                if parts and len(parts[0]) > 1:  # Skip single letter fragments
                    brand = parts[0]

        entries = []
        for _, row in group_rows.iterrows():
            link = ""
            if "product_link" in row.index and pd.notna(row["product_link"]):
                link = row["product_link"]
            elif "product_url" in row.index and pd.notna(row["product_url"]):
                link = row["product_url"]

            entries.append({
                "website": row.get("website", ""),
                "price": row.get("price", ""),
                "rating": row.get("rating", ""),
                "warranty_years": row.get("warranty_years", ""),
                "product_link": link,
            })

        try:
            entries.sort(key=lambda e: float(e["price"]))
        except Exception:
            pass

        rep_name = group_rows["product_name"].iloc[0]
        
        # Clean up duplicate brand in product name (e.g., "HP HP Pavilion" → "HP Pavilion")
        if brand:
            brand_lower = brand.lower()
            name_parts = rep_name.split()
            if name_parts and name_parts[0].lower() == brand_lower:
                # Check if second word is also brand, if so remove it
                if len(name_parts) > 1 and name_parts[1].lower() == brand_lower:
                    remaining = " ".join(name_parts[2:])
                    rep_name = f"{brand} {remaining}"
                elif len(name_parts) > 1 and name_parts[0].lower() == brand_lower:
                    # Just rebuild with clean format
                    remaining = " ".join(name_parts[1:])
                    rep_name = f"{brand} {remaining}"

        # collect representative spec fields if available
        specs = {}
        for key in ["model", "display", "processor", "ram", "storage", "camera", "battery", "product_id"]:
            if key in group_rows.columns and not group_rows[key].dropna().empty:
                specs[key] = str(group_rows[key].dropna().iloc[0])

        products.append({
            "product_name": rep_name,
            "image_url": image_url,
            "brand": brand,
            "entries": entries,
            "tokens": set(key.split()) if key else set(),
            "specs": specs,
        })

    return products


@app.route("/", methods=["GET", "POST"])
def index():
    # Allow access without login for demo purposes
    # if 'user' not in session:
    #     flash('Please login to access the price comparison tool.', 'info')
    #     return redirect(url_for('login'))
    
    print("DEBUG: Index route called")
    products = []
    if request.method == "POST":
        print("DEBUG: POST request received")
        search = request.form.get("product", "").strip()
        print(f"DEBUG: Search term: {search}")
        if search:
            # Use cached products (loads data once)
            all_products = get_all_products()
            
            if all_products:
                # normalize search term
                search_norm = normalize_name_for_exact(search)
                
                # Simple search: use precomputed normalized names for speed
                matched = []
                # ensure norms cached
                norms = _products_norm or [normalize_name_for_exact(p.get("product_name", "")) for p in all_products]
                for p_norm, p in zip(norms, all_products):
                    if search_norm in p_norm:
                        matched.append(p)
                        if len(matched) >= 3:  # Limit to 3 results
                            break

                # expected websites order
                expected_sites = ["Amazon", "Flipkart", "Meesho", "Myntra", "Snapdeal", "RelianceDigital", "Croma"]

                # load enrichment map for additional fields (discount, quality, reviews...)
                enriched_map = _load_enriched_map()
                print(f"DEBUG: enriched_map loaded with {len(enriched_map)} entries")
                
                # build ordered entries per expected site so UI shows one row per site
                products = []
                for p in matched:
                    entries = p.get("entries", [])
                    product_name = p.get("product_name", "")
                    
                    # Simple version: just show data from entries with enrichment
                    ordered = []
                    for site in expected_sites:
                        site_entries = [e for e in entries if str(e.get("website", "")).lower() == site.lower()]
                        if site_entries:
                            # Take the first entry for this site
                            item = dict(site_entries[0])
                            
                            # Format price properly - ensure it's a number first
                            price_raw = item.get("price")
                            try:
                                if price_raw:
                                    price_val = float(price_raw) if not isinstance(price_raw, (int, float)) else price_raw
                                    item["price_display"] = f"₹{int(price_val):,}"
                                    item["price"] = price_val
                                else:
                                    item["price_display"] = "N/A"
                                    item["price"] = None
                            except:
                                item["price_display"] = str(price_raw) if price_raw else "N/A"
                            
                            # Get enriched data (discount, quality, reviews)
                            key_e = f"{product_name}||{site}"
                            enriched = enriched_map.get(key_e)
                            
                            if enriched:
                                discount = enriched.get("discount_percent")
                                # Keep as number for template comparisons
                                item["discount_percent"] = int(discount) if discount and discount > 0 else 0
                                
                                quality_score = enriched.get("quality_score")
                                item["quality_score"] = int(quality_score) if quality_score else 0
                                
                                item["quality"] = enriched.get("quality", "-")
                                
                                reviews = enriched.get("reviews_count")
                                # Keep as number for template comparisons
                                item["reviews_count"] = int(reviews) if reviews else 0
                            else:
                                item["discount_percent"] = 0
                                item["quality_score"] = 0
                                item["quality"] = "-"
                                item["reviews_count"] = 0
                            
                            # Ensure we have rating
                            rating = item.get("rating")
                            item["rating"] = rating if rating else "-"
                            
                            # Ensure we have warranty
                            warranty = item.get("warranty_years")
                            item["warranty_years"] = warranty if warranty else "-"
                            
                            ordered.append(item)
                        else:
                            ordered.append({
                                "website": site,
                                "price": None,
                                "price_display": "N/A",
                                "rating": "-",
                                "warranty_years": "-",
                                "discount_percent": "-",
                                "quality_score": "-",
                                "quality": "-",
                                "reviews_count": "-",
                                "product_link": "",
                            })
                    
                    p["entries_ordered"] = ordered
                    products.append(p)

        return render_template('index.html', products=products)
    
    return render_template('index.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global registered_users
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Check if user exists and password matches
        if username in registered_users and registered_users[username] == password:
            session['user'] = username
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please register if you are new.', 'error')

    return render_template('login.html')


@app.route('/notifications', methods=['GET', 'POST'])
def notifications():
    if 'user' not in session:
        flash('Please login to view notifications.', 'info')
        return redirect(url_for('login'))

    meta = _load_users_meta()
    u = session.get('user')
    user_meta = meta.get(u, {})
    notifs = user_meta.get('notifications', [])

    # Optionally support clearing notifications via POST
    if request.method == 'POST':
        meta.setdefault(u, {})
        meta[u]['notifications'] = []
        _save_users_meta(meta)
        flash('Notifications cleared.', 'success')
        return redirect(url_for('notifications'))

    return render_template('notifications.html', notifications=notifs)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    global registered_users
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not username or not password:
            flash('Username and password are required.', 'error')
        elif len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
        elif len(password) < 4:
            flash('Password must be at least 4 characters long.', 'error')
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        elif username in registered_users:
            flash('Username already exists. Please choose another.', 'error')
        else:
            # Register new user
            registered_users[username] = password
            save_users(registered_users)
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


if __name__ == "__main__":
    # Use waitress for a production-like server when requested via env var.
    if os.environ.get("USE_WAITRESS") == "1":
        try:
            from waitress import serve
            port = int(os.environ.get("PORT", "5000"))
            serve(app, host="0.0.0.0", port=port)
        except Exception:
            # Fallback to Flask dev server if waitress isn't available
            app.run(debug=False, host="0.0.0.0")
    else:
        app.run(debug=True, host="0.0.0.0")
