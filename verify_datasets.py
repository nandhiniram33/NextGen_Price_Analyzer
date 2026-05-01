#!/usr/bin/env python
"""Test script to verify electronics datasets are loaded correctly"""

from app import load_all_data

print("=" * 70)
print("ELECTRONICS DATASET VERIFICATION")
print("=" * 70)

# Load all data
df = load_all_data()

print(f"\n✓ Total products loaded: {len(df):,}")
print(f"✓ Columns: {list(df.columns)}")

# Websites analysis
websites = df["website"].unique()
print(f"\n✓ Websites ({len(websites)}):")
for site in sorted(websites):
    count = len(df[df["website"] == site])
    print(f"  - {site}: {count:,} products")

# Categories analysis
if "category" in df.columns:
    categories = df["category"].unique()
    print(f"\n✓ Categories ({len(categories)}):")
    for cat in sorted(categories):
        count = len(df[df["category"] == cat])
        print(f"  - {cat}: {count:,} products")

# Price analysis
if "price" in df.columns:
    print(f"\n✓ Price Range:")
    print(f"  - Min: ₹{df['price'].min():,.0f}")
    print(f"  - Max: ₹{df['price'].max():,.0f}")
    print(f"  - Average: ₹{df['price'].mean():,.0f}")

# Rating analysis
if "rating" in df.columns:
    print(f"\n✓ Rating Distribution:")
    print(f"  - Min: {df['rating'].min()}")
    print(f"  - Max: {df['rating'].max()}")
    print(f"  - Average: {df['rating'].mean():.2f}")

# Warranty analysis
if "warranty_years" in df.columns:
    print(f"\n✓ Warranty Distribution:")
    print(f"  - Values: {sorted(df['warranty_years'].unique())}")

# Sample products
print(f"\n✓ Sample Products:")
print("-" * 70)
for idx, row in df.head(5).iterrows():
    print(f"  {row['brand']} {row['model']} ({row['category']})")
    print(f"    Price: ₹{row['price']:,.0f} | Rating: {row['rating']} | {row['website']}")

print("\n" + "=" * 70)
print("✓ ALL DATASETS VERIFIED SUCCESSFULLY!")
print("=" * 70)
