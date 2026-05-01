"""
notifier.py

Compare current enriched product prices with a previous snapshot and create
alerts when prices decrease or when a product has a large discount (sale).

This script writes a `dataset/price_snapshot.json` file and a `dataset/notifications.json`
file (per-run notifications). It can also inject simple notification entries
into a parallel `users_meta.json` file that holds user preferences and
notifications without modifying the project's original `users.json`.
"""
import os
import json
import time
from typing import Dict, Any
from pathlib import Path

from .enricher import enrich_all, ENRICHED_JSON


DATA_DIR = os.path.join(os.getcwd(), "dataset")
SNAPSHOT = os.path.join(DATA_DIR, "price_snapshot.json")
NOTIFICATIONS = os.path.join(DATA_DIR, "notifications.json")
USERS_META = os.path.join(os.getcwd(), "users_meta.json")


def _load_snapshot() -> Dict[str, Dict[str, Any]]:
    if os.path.exists(SNAPSHOT):
        try:
            with open(SNAPSHOT, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_snapshot(snapshot: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SNAPSHOT, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)


def _load_users_meta() -> Dict[str, Any]:
    if os.path.exists(USERS_META):
        try:
            with open(USERS_META, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_users_meta(users_meta: Dict[str, Any]):
    with open(USERS_META, "w", encoding="utf-8") as f:
        json.dump(users_meta, f, indent=2, ensure_ascii=False)


def run_once(min_drop_percent: float = 1.0, sale_threshold_pct: float = 20.0):
    # Ensure enriched data exists (this will write dataset/enriched_products.json)
    enriched = []
    if os.path.exists(ENRICHED_JSON):
        try:
            with open(ENRICHED_JSON, "r", encoding="utf-8") as f:
                enriched = json.load(f)
        except Exception:
            enriched = []

    if not enriched:
        enriched = enrich_all()

    # Build current price map keyed by product_name + website
    current = {}
    for e in enriched:
        key = f"{e.get('product_name','')}||{e.get('website','')}"
        current[key] = {
            "price": e.get("price"),
            "discount_percent": e.get("discount_percent", 0.0),
            "quality_score": e.get("quality_score", 0),
        }

    previous = _load_snapshot()

    notifications = []
    users_meta = _load_users_meta()

    # detect price decreases and sales
    for key, cur in current.items():
        prev = previous.get(key)
        if prev and prev.get("price") is not None and cur.get("price") is not None:
            try:
                prevp = float(prev.get("price"))
                curp = float(cur.get("price"))
                if curp < prevp:
                    drop_pct = (prevp - curp) / prevp * 100.0
                    if drop_pct >= min_drop_percent:
                        notifications.append({
                            "type": "price_drop",
                            "product_site": key,
                            "old_price": prevp,
                            "new_price": curp,
                            "drop_pct": round(drop_pct, 2),
                            "time": int(time.time())
                        })
                # sale detection
                if cur.get("discount_percent", 0.0) >= sale_threshold_pct:
                    notifications.append({
                        "type": "sale",
                        "product_site": key,
                        "discount_percent": cur.get("discount_percent"),
                        "time": int(time.time())
                    })
            except Exception:
                continue

    # Persist notifications and snapshot
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(NOTIFICATIONS, "w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # Update users_meta with notifications for all users (simple broadcast model)
    if notifications:
        for uname, meta in users_meta.items():
            meta.setdefault("notifications", [])
            meta["notifications"].extend(notifications)
        _save_users_meta(users_meta)

    # Save current as new snapshot
    _save_snapshot(current)
    return notifications


if __name__ == "__main__":
    print("Running notifier: comparing prices and writing dataset/notifications.json and users_meta.json")
    notifs = run_once()
    print(f"Found {len(notifs)} notifications.")
