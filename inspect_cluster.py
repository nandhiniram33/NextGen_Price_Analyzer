import os, sys
# Ensure project root is on sys.path so we can import `app`
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

from app import load_all_data, build_products_list

# Load products and find HP Pavilion clusters

df = load_all_data()
products = build_products_list(df)

matches = [p for p in products if 'hp pavilion' in p.get('product_name','').lower()]
print(f"Found {len(matches)} matching clusters for 'HP Pavilion'\n")
for i, p in enumerate(matches[:5], start=1):
    print(f"--- Cluster {i}: {p.get('product_name')} ---")
    entries = p.get('entries', [])
    for e in entries[:20]:
        print(repr(e))
    print('\nOrdered (expected) mapping sample:')
    # Re-run mapping logic similar to app.index to show ordered selection
    expected_sites = ["Amazon", "Flipkart", "Meesho", "Myntra", "Snapdeal", "RelianceDigital", "Croma"]
    # Replicate the improved mapping: choose minimum-price entry per website
    site_groups = {}
    for e in entries:
        key_site = str(e.get('website','')).strip().lower()
        site_groups.setdefault(key_site, []).append(e)

    def pval(x):
        try:
            return float(x.get('price'))
        except Exception:
            return None

    chosen_map = {}
    for key_site, group in site_groups.items():
        try:
            chosen = min(group, key=lambda x: pval(x) if pval(x) is not None else float('inf'))
        except Exception:
            chosen = group[-1]
        chosen_map[key_site] = chosen

    for site in expected_sites:
        key = site.lower()
        item = chosen_map.get(key)
        values = [pval(x) for x in site_groups.get(key, [])]
        print(site, 'chosen ->', item and item.get('price'), 'all_prices ->', values[:8])
    print('\n')

print('Done')
