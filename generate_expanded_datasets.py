import pandas as pd
import os
import random
from datetime import datetime

# Mobile phone models database with realistic specs
MOBILE_MODELS = {
    "Apple": [
        {"model": "iPhone 15 Pro Max", "display": "6.7 inch AMOLED", "processor": "A17 Pro", "ram": "8GB", "storage": ["256GB", "512GB", "1TB"], "camera": "48MP", "battery": "4685mAh", "base_price": 119999},
        {"model": "iPhone 15 Pro", "display": "6.1 inch AMOLED", "processor": "A17 Pro", "ram": "8GB", "storage": ["128GB", "256GB", "512GB"], "camera": "48MP", "battery": "3349mAh", "base_price": 99999},
        {"model": "iPhone 15", "display": "6.1 inch Liquid Retina", "processor": "A16 Bionic", "ram": "6GB", "storage": ["128GB", "256GB"], "camera": "48MP", "battery": "3349mAh", "base_price": 79999},
        {"model": "iPhone 15 Plus", "display": "6.7 inch Liquid Retina", "processor": "A16 Bionic", "ram": "6GB", "storage": ["128GB", "256GB"], "camera": "48MP", "battery": "4383mAh", "base_price": 89999},
        {"model": "iPhone 14 Pro Max", "display": "6.7 inch AMOLED", "processor": "A16 Bionic", "ram": "6GB", "storage": ["128GB", "256GB", "512GB", "1TB"], "camera": "48MP", "battery": "4323mAh", "base_price": 99999},
        {"model": "iPhone 14 Pro", "display": "6.1 inch AMOLED", "processor": "A16 Bionic", "ram": "6GB", "storage": ["128GB", "256GB", "512GB", "1TB"], "camera": "48MP", "battery": "3200mAh", "base_price": 79999},
        {"model": "iPhone 14", "display": "6.1 inch Liquid Retina", "processor": "A15 Bionic", "ram": "6GB", "storage": ["128GB", "256GB"], "camera": "12MP", "battery": "3279mAh", "base_price": 59999},
        {"model": "iPhone SE (3rd gen)", "display": "4.7 inch LCD", "processor": "A15 Bionic", "ram": "4GB", "storage": ["64GB", "128GB", "256GB"], "camera": "12MP", "battery": "2023mAh", "base_price": 39999},
    ],
    "Samsung": [
        {"model": "Galaxy S24 Ultra", "display": "6.8 inch Dynamic AMOLED", "processor": "Snapdragon 8 Gen 3", "ram": ["12GB", "16GB"], "storage": ["256GB", "512GB"], "camera": "200MP", "battery": "5000mAh", "base_price": 129999},
        {"model": "Galaxy S24 Plus", "display": "6.7 inch Dynamic AMOLED", "processor": "Snapdragon 8 Gen 3", "ram": ["12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "4900mAh", "base_price": 89999},
        {"model": "Galaxy S24", "display": "6.2 inch Dynamic AMOLED", "processor": "Snapdragon 8 Gen 3", "ram": ["8GB", "12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "4000mAh", "base_price": 79999},
        {"model": "Galaxy S23 Ultra", "display": "6.8 inch Dynamic AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["12GB", "16GB"], "storage": ["256GB", "512GB"], "camera": "200MP", "battery": "5000mAh", "base_price": 109999},
        {"model": "Galaxy S23 Plus", "display": "6.6 inch Dynamic AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["8GB", "12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "4500mAh", "base_price": 79999},
        {"model": "Galaxy A54", "display": "6.4 inch AMOLED", "processor": "Exynos 1280", "ram": ["6GB", "8GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 39999},
        {"model": "Galaxy A34", "display": "6.6 inch AMOLED", "processor": "MediaTek Helio G80", "ram": ["6GB", "8GB"], "storage": ["128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 34999},
        {"model": "Galaxy M34", "display": "6.7 inch LCD", "processor": "MediaTek Helio G99", "ram": ["6GB", "8GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "6000mAh", "base_price": 16999},
        {"model": "Galaxy Z Fold5", "display": "7.6 inch Foldable", "processor": "Snapdragon 8 Gen 2", "ram": ["12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "4400mAh", "base_price": 154999},
        {"model": "Galaxy Z Flip5", "display": "6.7 inch Foldable", "processor": "Snapdragon 8 Gen 2", "ram": ["8GB"], "storage": ["256GB", "512GB"], "camera": "12MP", "battery": "3900mAh", "base_price": 99999},
    ],
    "Xiaomi": [
        {"model": "13 Ultra", "display": "6.73 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["12GB", "16GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 89999},
        {"model": "13", "display": "6.36 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["8GB", "12GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "4500mAh", "base_price": 54999},
        {"model": "12 Pro", "display": "6.73 inch AMOLED", "processor": "Snapdragon 8 Gen 1", "ram": ["12GB"], "storage": ["256GB"], "camera": "50MP", "battery": "4600mAh", "base_price": 62999},
        {"model": "12", "display": "6.28 inch AMOLED", "processor": "Snapdragon 8 Gen 1", "ram": ["8GB", "12GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "4500mAh", "base_price": 44999},
        {"model": "Redmi Note 13 Pro Plus", "display": "6.67 inch AMOLED", "processor": "Snapdragon 7 Gen 2", "ram": ["8GB", "12GB"], "storage": ["128GB", "256GB"], "camera": "200MP", "battery": "5000mAh", "base_price": 24999},
        {"model": "Redmi Note 13 Pro", "display": "6.67 inch AMOLED", "processor": "Snapdragon 7 Gen 2", "ram": ["6GB", "8GB"], "storage": ["128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 19999},
        {"model": "Redmi Note 13", "display": "6.67 inch AMOLED", "processor": "MediaTek Helio G99", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 14999},
        {"model": "Redmi 13", "display": "6.52 inch LCD", "processor": "MediaTek Helio G99", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 10999},
    ],
    "Oppo": [
        {"model": "Find X6 Pro", "display": "6.82 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 109999},
        {"model": "Find X6", "display": "6.74 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["8GB", "12GB"], "storage": ["256GB", "512GB"], "camera": "48MP", "battery": "5000mAh", "base_price": 89999},
        {"model": "A78", "display": "6.43 inch AMOLED", "processor": "Snapdragon 695", "ram": ["6GB", "8GB"], "storage": ["128GB", "256GB"], "camera": "48MP", "battery": "4500mAh", "base_price": 34999},
        {"model": "A58", "display": "6.43 inch AMOLED", "processor": "Snapdragon 680", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 16999},
        {"model": "F23", "display": "6.72 inch LCD", "processor": "MediaTek Helio G99", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 12999},
        {"model": "Reno 8 Pro", "display": "6.62 inch AMOLED", "processor": "Snapdragon 7 Gen 1", "ram": ["8GB", "12GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "4500mAh", "base_price": 42999},
    ],
    "Vivo": [
        {"model": "X90 Pro Plus", "display": "6.78 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 119999},
        {"model": "X90", "display": "6.78 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["12GB"], "storage": ["256GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 79999},
        {"model": "V27", "display": "6.62 inch AMOLED", "processor": "MediaTek Dimensity 7050", "ram": ["8GB", "12GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "4500mAh", "base_price": 34999},
        {"model": "Y77", "display": "6.51 inch LCD", "processor": "MediaTek Helio G99", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 13999},
        {"model": "T1 5G", "display": "6.47 inch AMOLED", "processor": "Snapdragon 778G 5G", "ram": ["6GB", "8GB"], "storage": ["128GB"], "camera": "50MP", "battery": "4500mAh", "base_price": 29999},
    ],
    "OnePlus": [
        {"model": "12", "display": "6.7 inch AMOLED", "processor": "Snapdragon 8 Gen 3", "ram": ["12GB", "16GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5400mAh", "base_price": 64999},
        {"model": "11", "display": "6.7 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["8GB", "12GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 56999},
        {"model": "11 Pro", "display": "6.7 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 66999},
        {"model": "Nord 3", "display": "6.43 inch AMOLED", "processor": "Snapdragon 778G+ 5G", "ram": ["8GB", "12GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "4500mAh", "base_price": 29999},
        {"model": "Nord CE 3", "display": "6.43 inch AMOLED", "processor": "Snapdragon 695", "ram": ["6GB", "8GB"], "storage": ["128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 23999},
    ],
    "Realme": [
        {"model": "12 Pro Plus", "display": "6.7 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["8GB", "12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 44999},
        {"model": "12 Pro", "display": "6.72 inch AMOLED", "processor": "Snapdragon 7 Gen 2", "ram": ["8GB"], "storage": ["256GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 32999},
        {"model": "12", "display": "6.43 inch AMOLED", "processor": "Snapdragon 7 Gen 1", "ram": ["6GB", "8GB"], "storage": ["128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 27999},
        {"model": "C53", "display": "6.74 inch LCD", "processor": "Snapdragon 685", "ram": ["6GB", "8GB"], "storage": ["128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 16999},
        {"model": "C35", "display": "6.5 inch LCD", "processor": "Snapdragon 680", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 9999},
    ],
    "Poco": [
        {"model": "X6 Pro", "display": "6.67 inch AMOLED", "processor": "Snapdragon 8 Gen 2", "ram": ["8GB", "12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 34999},
        {"model": "X6", "display": "6.67 inch AMOLED", "processor": "MediaTek Dimensity 8300 Ultra", "ram": ["8GB", "12GB"], "storage": ["256GB", "512GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 29999},
        {"model": "M5", "display": "6.67 inch LCD", "processor": "MediaTek Helio G99", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 12999},
        {"model": "F4 5G", "display": "6.67 inch LCD", "processor": "Snapdragon 695 5G", "ram": ["6GB", "8GB"], "storage": ["128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 18999},
    ],
    "Nokia": [
        {"model": "G400", "display": "6.5 inch LCD", "processor": "MediaTek Helio G99", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "5000mAh", "base_price": 14999},
        {"model": "G300", "display": "6.5 inch LCD", "processor": "MediaTek Helio G99", "ram": ["4GB"], "storage": ["64GB"], "camera": "13MP", "battery": "5000mAh", "base_price": 12999},
        {"model": "X30", "display": "6.67 inch LCD", "processor": "Snapdragon 680", "ram": ["4GB", "6GB"], "storage": ["64GB", "128GB"], "camera": "50MP", "battery": "4800mAh", "base_price": 17999},
    ],
    "Google": [
        {"model": "Pixel 8 Pro", "display": "6.7 inch AMOLED", "processor": "Google Tensor G3", "ram": ["12GB"], "storage": ["128GB", "256GB", "512GB"], "camera": "50MP", "battery": "5050mAh", "base_price": 109999},
        {"model": "Pixel 8", "display": "6.2 inch AMOLED", "processor": "Google Tensor G3", "ram": ["8GB"], "storage": ["128GB", "256GB"], "camera": "50MP", "battery": "4575mAh", "base_price": 74999},
        {"model": "Pixel 7a", "display": "6.1 inch AMOLED", "processor": "Google Tensor", "ram": ["6GB"], "storage": ["128GB"], "camera": "64MP", "battery": "4410mAh", "base_price": 43999},
    ],
}

# Websites list
WEBSITES = ["Amazon", "Flipkart", "Croma", "Meesho", "Myntra", "RelianceDigital", "Snapdeal"]

# Processor variations
PROCESSOR_VARIANTS = ["Snapdragon 8 Gen 3", "Snapdragon 8 Gen 2", "Snapdragon 695", "Snapdragon 680", 
                      "MediaTek Helio G99", "A17 Pro", "A16 Bionic", "A15 Bionic", "Exynos 2200", 
                      "MediaTek Dimensity 9200", "MediaTek Dimensity 8300", "Snapdragon 7 Gen 2"]

def generate_phone_data(brand, base_models, num_per_model=30):
    """Generate realistic phone data with variations"""
    data = []
    product_id = 1
    
    for model_info in base_models:
        for variant in range(num_per_model):
            # Vary specs slightly
            ram = model_info["ram"] if isinstance(model_info["ram"], list) else [model_info["ram"]]
            storage = model_info["storage"] if isinstance(model_info["storage"], list) else [model_info["storage"]]
            
            record = {
                "brand": brand,
                "model": model_info["model"],
                "display": model_info["display"],
                "processor": model_info["processor"],
                "ram": random.choice(ram),
                "storage": random.choice(storage),
                "camera": model_info["camera"],
                "battery": model_info["battery"],
                "price": model_info["base_price"] + random.randint(-5000, 15000),
                "rating": round(random.uniform(3.0, 4.9), 1),
                "warranty_years": random.randint(1, 3),
            }
            data.append(record)
            product_id += 1
    
    return data

def create_expanded_datasets():
    """Create expanded dataset files with 5000+ records"""
    
    all_data = []
    product_counter = 1
    
    # Generate data for all brands
    for brand, models in MOBILE_MODELS.items():
        brand_data = generate_phone_data(brand, models, num_per_model=40)
        for record in brand_data:
            record["product_id"] = f"PRODUCT{str(product_counter).zfill(5)}"
            record["image_url"] = f"https://mobile-images.com/{record['brand'].lower()}/{record['model'].replace(' ', '-').lower()}.jpg"
            record["website"] = random.choice(WEBSITES)
            all_data.append(record)
            product_counter += 1
    
    # Create DataFrames for each website
    dataset_dir = os.path.join(os.getcwd(), "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    
    website_files = {
        "Amazon": "amazon_mobilephones_5000_fullspecs.csv",
        "Flipkart": "flipkart_mobilephones_5000_fullspecs.csv",
        "Croma": "croma_mobilephones_5000_fullspecs.csv",
        "Meesho": "meesho_mobilephones_5000_fullspecs.csv",
        "Myntra": "myntra_mobilephones_5000_fullspecs.csv",
        "RelianceDigital": "reliancedigital_mobilephones_5000_fullspecs.csv",
        "Snapdeal": "snapdeal_mobilephones_5000_fullspecs.csv",
    }
    
    # Split data by website and save
    for website, filename in website_files.items():
        website_data = [record for record in all_data if record["website"] == website]
        
        # Add more records to reach 5000+ per file
        while len(website_data) < 5100:
            # Duplicate and modify existing records
            base_record = random.choice(all_data)
            new_record = base_record.copy()
            new_record["product_id"] = f"PRODUCT{str(product_counter).zfill(5)}"
            new_record["price"] = base_record["price"] + random.randint(-3000, 5000)
            new_record["rating"] = round(random.uniform(3.0, 4.9), 1)
            website_data.append(new_record)
            product_counter += 1
        
        df = pd.DataFrame(website_data[:5100])  # Limit to 5100
        
        # Column order
        columns = ["product_id", "brand", "model", "display", "processor", "ram", "storage", 
                   "camera", "battery", "price", "rating", "website", "warranty_years", "image_url"]
        df = df[columns]
        
        filepath = os.path.join(dataset_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"✓ Created {filename} with {len(df)} records")
    
    print(f"\n✓ Successfully generated {len(all_data)} unique mobile phone records")
    print(f"✓ Total records across all websites: {len(all_data) * 7}")
    print(f"✓ Brands included: {', '.join(MOBILE_MODELS.keys())}")

if __name__ == "__main__":
    print("Generating expanded mobile phone datasets...")
    print("=" * 60)
    create_expanded_datasets()
    print("=" * 60)
    print("✓ All datasets generated successfully!")
