import csv
import os
import random
import urllib.parse

OUTPUT_DIR = "dataset"  # Changed to match app.py
NUM_PRODUCTS = 4000
WEBSITES = [
    ("Amazon", "amazon"),
    ("Flipkart", "flipkart"),
    ("Meesho", "meesho"),
    ("Myntra", "myntra"),
    ("Snapdeal", "snapdeal"),
    ("RelianceDigital", "reliancedigital"),
    ("Croma", "croma"),
]

# Real mobile models for each brand
BRAND_MODELS = {
    "Samsung": [
        "Galaxy S23", "Galaxy S23+", "Galaxy S23 Ultra", "Galaxy S22", "Galaxy S22+", "Galaxy S22 Ultra",
        "Galaxy A54", "Galaxy A34", "Galaxy A14", "Galaxy M34", "Galaxy M14", "Galaxy F54",
        "Galaxy Z Fold5", "Galaxy Z Flip5", "Galaxy Note20", "Galaxy A73", "Galaxy A53", "Galaxy A33",
        "Galaxy M53", "Galaxy M33", "Galaxy F23", "Galaxy F13", "Galaxy A23", "Galaxy A13",
        "Galaxy S21", "Galaxy S21+", "Galaxy S21 Ultra", "Galaxy Z Fold4", "Galaxy Z Flip4",
        "Galaxy A72", "Galaxy A52", "Galaxy A32", "Galaxy M52", "Galaxy M32", "Galaxy F42",
        "Galaxy A22", "Galaxy A12", "Galaxy M22", "Galaxy M12", "Galaxy F22", "Galaxy F12"
    ],
    "Xiaomi": [
        "13", "13 Pro", "13 Ultra", "12", "12 Pro", "12S Ultra", "11T", "11T Pro",
        "Poco X4 Pro", "Poco X3 Pro", "Poco M4 Pro", "Poco C31", "Redmi Note 12", "Redmi Note 12 Pro",
        "Redmi 12", "Redmi 12C", "Redmi A1", "Redmi 10", "Redmi 10A", "Redmi Note 11", "Redmi Note 11 Pro",
        "Redmi Note 10", "Redmi Note 10 Pro", "Redmi 9", "Redmi 9A", "Redmi Note 9", "Redmi Note 9 Pro",
        "Mi 11", "Mi 11 Ultra", "Mi 10T", "Mi 10T Pro", "Poco F3", "Poco F2 Pro", "Poco M3", "Poco M2"
    ],
    "Realme": [
        "10 Pro+", "10 Pro", "10", "9 Pro+", "9 Pro", "9", "8 Pro", "8", "Narzo 50", "Narzo 50A",
        "Narzo 50 Pro", "Narzo 30", "C35", "C33", "C30", "C21", "C11", "GT 2", "GT Neo 3", "GT Master Edition",
        "X7 Pro", "X7", "X3 SuperZoom", "7 Pro", "7", "6 Pro", "6", "5 Pro", "5", "XT", "3 Pro"
    ],
    "OnePlus": [
        "11", "11R", "10 Pro", "10", "9 Pro", "9", "8 Pro", "8", "8T", "Nord CE 2", "Nord CE", "Nord N20",
        "Nord N10", "Nord 2", "Nord", "7 Pro", "7", "7T", "7T Pro", "6T", "6", "5T", "5"
    ],
    "OPPO": [
        "Find X5 Pro", "Find X5", "Find X3 Pro", "Find X3", "Reno 8 Pro", "Reno 8", "Reno 7 Pro", "Reno 7",
        "A96", "A77", "A57", "A16", "A15", "F21 Pro", "F19 Pro", "F19", "F17 Pro", "F17", "F15", "K10",
        "K9", "A94", "A74", "A54", "A31", "F11 Pro", "F11", "F9 Pro", "F9", "A9", "A5"
    ],
    "Vivo": [
        "X80 Pro", "X80", "X70 Pro+", "X70 Pro", "X70", "S15 Pro", "S15", "T1", "T1x", "Y75", "Y55",
        "Y35", "Y21", "Y15", "V25 Pro", "V25", "V23 Pro", "V23", "Y100", "Y75", "Y33T", "Y22", "Y16",
        "V21", "V20", "Y20", "Y12", "V19", "V17 Pro", "V15 Pro", "Y91", "Y81", "Y71"
    ],
    "Motorola": [
        "Edge 30 Ultra", "Edge 30 Pro", "Edge 30", "Edge 20 Pro", "Edge 20", "Moto G Stylus", "Moto G Power",
        "Moto G Play", "Moto E32", "Moto E22", "Moto G82", "Moto G72", "Moto G62", "Moto G42", "Moto G32",
        "Moto G22", "Moto G13", "Moto G12", "Moto E13", "Moto E7", "Moto G60", "Moto G40", "Moto G31",
        "Moto G21", "Moto E20", "Moto E6", "Moto G9 Power", "Moto G9 Play", "Moto G9 Plus", "Moto G8 Power"
    ],
    "Apple": [
        "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14", "iPhone 14 Plus", "iPhone 13 Pro Max", "iPhone 13 Pro",
        "iPhone 13", "iPhone 13 mini", "iPhone 12 Pro Max", "iPhone 12 Pro", "iPhone 12", "iPhone 12 mini",
        "iPhone 11 Pro Max", "iPhone 11 Pro", "iPhone 11", "iPhone SE (3rd generation)", "iPhone XR", "iPhone XS Max",
        "iPhone XS", "iPhone X", "iPhone 8 Plus", "iPhone 8", "iPhone 7 Plus", "iPhone 7", "iPhone 6s Plus", "iPhone 6s"
    ],
    "Poco": [
        "X4 Pro 5G", "X4 GT", "X3 Pro", "X3 GT", "M4 Pro 5G", "M4 Pro", "M3 Pro 5G", "C31", "F3 GT", "F2 Pro",
        "M2 Pro", "M2", "C3", "X2", "F1", "M3", "C40", "M5", "X5 Pro", "X5", "M5s", "C50", "M4 5G"
    ],
    "Infinix": [
        "Note 30", "Note 30 Pro", "Note 12", "Note 12 Pro", "Hot 20", "Hot 20 Play", "Smart 7", "Smart 7 HD",
        "Zero 20", "Zero 20 Pro", "Note 11 Pro", "Note 11", "Hot 11 Play", "Hot 11", "Smart 6", "Smart 6 HD",
        "Zero 5G", "Note 7", "Hot 9 Play", "Hot 9", "S5 Pro", "S5", "Hot 8", "Note 5", "Hot 7 Pro", "Hot 7"
    ],
    "Tecno": [
        "Camon 19 Pro", "Camon 19", "Spark 9 Pro", "Spark 9", "Pova 4", "Pova 4 Pro", "Phantom X2", "Phantom X2 Pro",
        "Camon 18 Premier", "Camon 18 Pro", "Camon 18", "Spark 8 Pro", "Spark 8", "Pova 3", "Pova 2", "Phantom X",
        "Camon 17 Pro", "Camon 17", "Spark 7 Pro", "Spark 7", "Pova Neo", "Camon 16 Premier", "Camon 16 Pro",
        "Camon 16", "Spark 6 Go", "Spark 5 Pro", "Spark 5", "Camon 15 Pro", "Camon 15", "Spark 4"
    ],
    "Honor": [
        "90", "80 Pro", "70", "50", "X9", "X8", "X7", "X6", "Play 30", "Play 20", "Magic 4 Pro", "Magic 4",
        "View 30 Pro", "View 30", "50 Lite", "30S", "20S", "10 Lite", "9X", "8X", "7X", "6X", "Play 9A", "Play 8A"
    ],
    "Nokia": [
        "X30", "X20", "G60", "G50", "G22", "G11", "G10", "C31", "C21 Plus", "C21", "C20", "C10", "C01 Plus",
        "8.3", "7.2", "6.2", "5.4", "3.4", "2.4", "1.4", "9 PureView", "8 Sirocco", "7 Plus", "6", "5", "3", "2"
    ],
    "LG": [
        "Velvet", "Wing", "V60 ThinQ", "V50 ThinQ", "G8 ThinQ", "G7 ThinQ", "V40 ThinQ", "V35 ThinQ", "G6", "G5",
        "V30", "V20", "G4", "G3", "G2", "Optimus G", "Nexus 5X", "Nexus 4", "Stylo 6", "Stylo 5", "K92", "K62",
        "K52", "K41S", "K40S", "K22", "Q92", "Q70", "Q60", "Q51"
    ],
    "Sony": [
        "Xperia 1 IV", "Xperia 5 IV", "Xperia 10 IV", "Xperia Pro-I", "Xperia 1 III", "Xperia 5 III", "Xperia 10 III",
        "Xperia 1 II", "Xperia 5 II", "Xperia 10 II", "Xperia 1", "Xperia 5", "Xperia 10", "Xperia XZ3", "Xperia XZ2",
        "Xperia XZ1", "Xperia XZs", "Xperia XZ", "Xperia X", "Xperia Z5 Premium", "Xperia Z5", "Xperia Z4", "Xperia Z3"
    ],
    "itel": [
        "A58", "A56", "A48", "A46", "A25", "A23", "S23", "S18", "P40", "P38", "P37", "P33", "Vision 3", "Vision 2",
        "Vision 1", "A14", "A12", "S16", "S15", "P15", "P12", "A05s", "A04", "S11", "P11", "A11", "S661W", "A661W"
    ],
    "Asus": [
        "Zenfone 9", "Zenfone 8", "ROG Phone 6", "ROG Phone 6 Pro", "Zenfone 7 Pro", "Zenfone 7", "ROG Phone 5",
        "ROG Phone 5 Pro", "Zenfone 6", "Zenfone 5", "Zenfone 4", "Zenfone 3", "Zenfone 2", "Zenfone", "Padfone",
        "Zenfone Max Pro M1", "Zenfone Max M1", "Zenfone Lite L1", "Zenfone Go", "Zenfone Selfie", "Zenfone Zoom",
        "Zenfone AR", "Zenfone 5 Lite", "Zenfone 4 Selfie", "Zenfone 3 Max", "Zenfone 3 Laser", "Zenfone 2 Laser"
    ],
    "Lenovo": [
        "Legion Phone Duel 2", "Legion Phone Duel", "K13 Note", "K13", "K12 Note", "K12 Pro", "K12", "K11 Note",
        "K10 Note", "K10", "K9", "K8 Note", "K8", "K6 Power", "K6 Note", "K5 Note", "K5 Play", "K4 Note", "Vibe K5",
        "Vibe P1", "Vibe S1", "Vibe X3", "Vibe Z2 Pro", "Vibe Z2", "A7000", "A6000", "A5000", "S90", "P90"
    ],
    "ZTE": [
        "Axon 40 Ultra", "Axon 30 Ultra", "Axon 30", "Axon 20", "Blade V40", "Blade V30", "Blade A72", "Blade A52",
        "Blade A32", "Blade A31", "Blade L210", "Nubia Red Magic 7", "Nubia Red Magic 7 Pro", "Nubia Z40 Pro",
        "Nubia Z30 Pro", "Nubia Play", "Nubia Red Magic 6", "Nubia Red Magic 6 Pro", "Nubia Z35", "Nubia Z30"
    ],
    "Sharp": [
        "Aquos R6", "Aquos R5G", "Aquos Zero2", "Aquos Sense6", "Aquos Sense5G", "Aquos Wish", "Aquos R3", "Aquos R2",
        "Aquos S3", "Aquos S2", "Aquos SH-M10", "Aquos SH-M09", "Aquos SH-M08", "Aquos SH-M07", "Aquos SH-M06",
        "Aquos SH-M05", "Aquos SH-M04", "Aquos SH-M03", "Aquos SH-M02", "Aquos SH-M01"
    ]
}

random.seed(42)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Collect all models
all_models = []
for brand, models_list in BRAND_MODELS.items():
    for model in models_list:
        all_models.append((f"{brand} {model}", brand))

# Duplicate to reach NUM_PRODUCTS
models = (all_models * (NUM_PRODUCTS // len(all_models) + 1))[:NUM_PRODUCTS]
random.shuffle(models)

print(f"Using {len(models)} mobile models (duplicated from {len(all_models)} unique)")

# placeholder image helper
def image_url_for():
    text = urllib.parse.quote_plus(name)
    return f"https://via.placeholder.com/300?text={text}"

# price baseline for phones
BASE_PRICE = (7000, 120000)

for display_name, short in WEBSITES:
    filename = os.path.join(OUTPUT_DIR, f"{short}_mobilephones_{NUM_PRODUCTS}_fullspecs.csv")

    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["product_id", "brand", "model", "display", "processor", "ram", "storage", "camera", "battery", "price", "rating", "website", "warranty_years", "image_url"])

        for idx, (full_model, brand) in enumerate(models, 1):
            # Generate specs
            display = random.choice(["6.1 inch", "6.4 inch", "6.5 inch", "6.7 inch", "6.8 inch", "5.5 inch", "5.8 inch"])
            processor = random.choice(["Snapdragon 8 Gen 2", "Snapdragon 8 Gen 1", "Dimensity 9200", "A15 Bionic", "Exynos 2200", "MediaTek Helio G99", "Snapdragon 695"])
            ram = random.choice(["4GB", "6GB", "8GB", "12GB", "16GB"])
            storage = random.choice(["64GB", "128GB", "256GB", "512GB", "1TB"])
            camera = random.choice(["12MP", "48MP", "64MP", "108MP", "50MP + 12MP + 10MP"])
            battery = random.choice(["4000mAh", "4500mAh", "5000mAh", "6000mAh", "4500mAh with 65W fast charging"])

            base = random.randint(BASE_PRICE[0], BASE_PRICE[1])
            mult = random.uniform(0.90, 1.12)
            price = int(base * mult)
            rating = round(random.uniform(3.0, 4.9), 1)
            warranty = random.choice([0, 1, 1, 2])  # 0,1,2 years, more 1

            product_id = f"{short.upper()}{idx:04d}"
            model_name = full_model.split(' ', 1)[1]  # Remove brand from model
            image_url = image_url_for(full_model)

            writer.writerow([product_id, brand, model_name, display, processor, ram, storage, camera, battery, price, rating, display_name, warranty, image_url])

    print(f"Wrote: {filename}")

print("Done: generated real mobile datasets for all websites.")
