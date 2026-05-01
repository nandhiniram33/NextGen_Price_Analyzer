"""
enricher.py

Loads dataset CSVs from the project's `dataset/` folder and produces an
enriched JSON/CSV output with additional computed fields per product and per
website entry: `discount`, `quality_score`, `warranty`, `reviews_count`,
`feedback` (placeholder), and `features` inferred from specs.

This module is intentionally standalone and does not modify existing project
files; it writes outputs into `dataset/enriched_products.json` and
`dataset/enriched_products.csv`.
"""
import os
import glob
import json
import random
from typing import List, Dict, Any
import pandas as pd


DATA_DIR = os.path.join(os.getcwd(), "dataset")
ENRICHED_JSON = os.path.join(DATA_DIR, "enriched_products.json")
ENRICHED_CSV = os.path.join(DATA_DIR, "enriched_products.csv")

# Per-website heuristics to bias reviews, quality and discount behaviour
WEBSITE_PROFILES = {
    "Amazon": {"review_mul": 1.3, "quality_bias": 1.02, "discount_bias": 1.0, "base_reviews": 300},
    "Flipkart": {"review_mul": 1.1, "quality_bias": 1.0, "discount_bias": 1.05, "base_reviews": 200},
    "Meesho": {"review_mul": 0.6, "quality_bias": 0.95, "discount_bias": 1.2, "base_reviews": 40},
    "Myntra": {"review_mul": 0.8, "quality_bias": 0.98, "discount_bias": 1.15, "base_reviews": 60},
    "Snapdeal": {"review_mul": 0.5, "quality_bias": 0.9, "discount_bias": 1.25, "base_reviews": 30},
    "RelianceDigital": {"review_mul": 0.7, "quality_bias": 1.0, "discount_bias": 1.0, "base_reviews": 50},
    "Croma": {"review_mul": 0.6, "quality_bias": 0.95, "discount_bias": 1.0, "base_reviews": 25},
}

def _quality_label(score: int) -> str:
    try:
        s = int(score)
    except Exception:
        return "Unknown"
    if s >= 85:
        return "Excellent"
    if s >= 70:
        return "Good"
    if s >= 50:
        return "Fair"
    return "Poor"


def _discover_csvs() -> List[str]:
    pattern = os.path.join(DATA_DIR, "*.csv")
    return [p for p in glob.glob(pattern) if os.path.isfile(p)]


def _infer_features_from_row(row: Dict[str, Any]) -> List[str]:
    features = set()
    # simple inference rules from common spec keys
    text = " ".join([str(row.get(k, "")) for k in ["display", "processor", "battery", "storage", "ram", "camera"]]).lower()
    if "oled" in text or "amoled" in text:
        features.add("oled_display")
    if "ips" in text:
        features.add("ips_display")
    if "fast" in text and "charge" in text:
        features.add("fast_charging")
    if "waterproof" in text or "ip67" in text or "ip68" in text:
        features.add("water_resistant")
    if "dual sim" in text or "sim" in text:
        features.add("dual_sim")
    if any(x in text for x in ["4gb", "6gb", "8gb", "12gb"]):
        features.add("ample_ram")
    if "ssd" in text or "nvme" in text:
        features.add("ssd_storage")
    return sorted(features)


def _compute_quality_score(rating, specs: Dict[str, Any]) -> int:
    # rating contributes up to 70, specs heuristics add up to 30
    try:
        r = float(rating)
    except Exception:
        r = 0.0
    score = min(max(int((r / 5.0) * 70), 0), 70)
    # simple heuristics
    if specs.get("ram"):
        try:
            ram_val = int(''.join([c for c in str(specs.get("ram")) if c.isdigit()]))
            if ram_val >= 8:
                score += 15
            elif ram_val >= 4:
                score += 8
        except Exception:
            pass
    if specs.get("battery"):
        try:
            bat = int(''.join([c for c in str(specs.get("battery")) if c.isdigit()]))
            if bat >= 4000:
                score += 10
            elif bat >= 3000:
                score += 5
        except Exception:
            pass
    return min(100, score)


def enrich_all(overwrite: bool = True) -> List[Dict[str, Any]]:
    csvs = _discover_csvs()
    if not csvs:
        return []

    dfs = []
    for p in csvs:
        try:
            d = pd.read_csv(p)
        except Exception:
            continue
        # ensure product_name exists
        if "product_name" not in d.columns:
            if "model" in d.columns:
                d["product_name"] = d["model"].astype(str)
            else:
                d["product_name"] = d.iloc[:, 0].astype(str)

        # ensure website
        if "website" not in d.columns:
            name = os.path.basename(p).lower()
            w = ""
            for site in ["amazon", "flipkart", "meesho", "myntra", "snapdeal", "reliancedigital", "croma"]:
                if site in name:
                    w = site.capitalize() if site != "reliancedigital" else "RelianceDigital"
                    break
            d["website"] = w

        dfs.append(d.copy())

    if not dfs:
        return []

    df = pd.concat(dfs, ignore_index=True, sort=False)

    enriched_products = []

    # group by product_name + website to ensure per-site entries
    gp = df.groupby([df["product_name"].astype(str), df["website"].astype(str)])
    for (pname, site), group in gp:
        for _, row in group.iterrows():
            specs = {}
            for k in ["model", "display", "processor", "ram", "storage", "camera", "battery", "product_id"]:
                if k in row.index and pd.notna(row[k]):
                    specs[k] = row[k]

            price = None
            try:
                price = float(row.get("price", None)) if row.get("price", None) not in ["", None] else None
            except Exception:
                price = None

            rating = row.get("rating", None)
            warranty = row.get("warranty_years", None) if "warranty_years" in row.index else None

            # discount calculation if original/old_price available
            discount = 0.0
            if "original_price" in row.index and pd.notna(row.get("original_price", None)) and price:
                try:
                    op = float(row.get("original_price"))
                    if op > 0:
                        discount = round((op - price) / op * 100, 2)
                except Exception:
                    discount = 0.0

            features = _infer_features_from_row(row.to_dict())
            # Apply website-specific adjustments
            profile = WEBSITE_PROFILES.get(str(site), {})
            review_mul = profile.get("review_mul", 0.8)
            quality_bias = profile.get("quality_bias", 1.0)
            discount_bias = profile.get("discount_bias", 1.0)
            base_rev = profile.get("base_reviews", 50)

            # Reviews count: prefer existing value if present, otherwise estimate
            existing_reviews = None
            if "reviews_count" in row.index and pd.notna(row.get("reviews_count", None)):
                try:
                    existing_reviews = int(row.get("reviews_count"))
                except Exception:
                    existing_reviews = None

            if existing_reviews is not None and existing_reviews >= 0:
                reviews_count = int(max(0, int(existing_reviews * review_mul)))
            else:
                # estimate from rating and profile base
                try:
                    rat = float(rating) if rating not in [None, "", "NaN"] else 0.0
                except Exception:
                    rat = 0.0
                # higher rating → more reviews likely; random noise for variety
                reviews_count = int(max(0, int(base_rev * (1 + (rat / 5.0))) + random.randint(-10, 50)))

            # Quality score: compute then bias by website
            raw_quality = _compute_quality_score(rating, specs)
            adjusted_quality = int(min(100, max(0, int(raw_quality * quality_bias))))
            quality_label = _quality_label(adjusted_quality)

            # Discount: apply a small site bias to observed discount
            final_discount = None
            try:
                if discount and float(discount) > 0:
                    final_discount = round(float(discount) * float(discount_bias), 2)
                else:
                    # simulate occasional deals for sites with higher discount_bias
                    if discount_bias >= 1.15 and random.random() < 0.08:
                        final_discount = round(random.uniform(10.0, 40.0), 2)
                    else:
                        final_discount = 0.0
            except Exception:
                final_discount = 0.0

            entry = {
                "product_name": str(pname),
                "website": str(site),
                "brand": row.get("brand", ""),
                "price": price,
                "rating": rating,
                "warranty_years": warranty,
                "discount_percent": final_discount,
                "quality_score": adjusted_quality,
                "quality": quality_label,
                "reviews_count": reviews_count,
                "feedback": [],
                "features": features,
                "specs": specs,
                "product_link": row.get("product_link", "") if "product_link" in row.index else "",
            }

            enriched_products.append(entry)

    # Optionally write outputs
    if overwrite:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(ENRICHED_JSON, "w", encoding="utf-8") as f:
                json.dump(enriched_products, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        try:
            # flatten for CSV writing
            rows = []
            for e in enriched_products:
                r = dict(e)
                r["features"] = ";".join(r.get("features", []))
                r.update({"specs_" + k: v for k, v in r.get("specs", {}).items()})
                r.pop("specs", None)
                rows.append(r)
            pd.DataFrame(rows).to_csv(ENRICHED_CSV, index=False)
        except Exception:
            pass

    return enriched_products


if __name__ == "__main__":
    print("Running enricher: generating enriched_products.json and CSV in dataset/")
    enriched = enrich_all()
    print(f"Enriched {len(enriched)} product entries.")
