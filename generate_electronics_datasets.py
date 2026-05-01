import csv
import os
import random
from datetime import datetime, timedelta

OUTPUT_DIR = "dataset"
NUM_PRODUCTS = 27000  # 27000 products per website
WEBSITES = [
    ("Amazon", "amazon"),
    ("Flipkart", "flipkart"),
    ("Meesho", "meesho"),
    ("Myntra", "myntra"),
    ("Snapdeal", "snapdeal"),
    ("RelianceDigital", "reliancedigital"),
    ("Croma", "croma"),
]

# Electronic categories with brands and models
ELECTRONICS_CATALOG = {
    "Smartphones": {
        "brands": {
            "Apple": ["iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14", "iPhone 13 Pro Max", "iPhone 13 Pro", 
                      "iPhone 13", "iPhone 12 Pro Max", "iPhone 12 Pro", "iPhone 12", "iPhone SE"],
            "Samsung": ["Galaxy S23 Ultra", "Galaxy S23+", "Galaxy S23", "Galaxy S22", "Galaxy A54", 
                        "Galaxy A34", "Galaxy M34", "Galaxy Z Fold5", "Galaxy Z Flip5", "Galaxy Note20"],
            "Xiaomi": ["13 Pro", "13", "12T Pro", "12S Ultra", "11T Pro", "Poco X5", "Redmi Note 12 Pro", 
                       "Redmi 12", "Poco M4 Pro", "Redmi 11 Pro"],
            "OnePlus": ["11", "11R", "10 Pro", "10T", "9 Pro", "Nord CE 2", "Nord CE", "Nord N20", "Nord N10", "Nord 2"],
            "Realme": ["10 Pro+", "10 Pro", "10", "9 Pro+", "9 Pro", "Narzo 50", "Narzo 30", "C35", "C33", "C30"],
            "OPPO": ["Find X5 Pro", "Find X5", "Reno 8 Pro", "Reno 8", "A96", "A77", "F21 Pro", "F19 Pro", "A57", "A16"],
            "Vivo": ["X80 Pro", "X80", "S15 Pro", "S15", "T1", "Y75", "Y55", "V25 Pro", "V25", "V23 Pro"],
            "Motorola": ["Edge 30 Ultra", "Edge 30 Pro", "Edge 30", "Moto G Stylus", "Moto G Power", 
                         "Moto G Play", "Moto G82", "Moto G72", "Moto G62", "Moto E32"],
        },
        "price_range": (8000, 150000),
        "rating_base": 3.8,
    },
    "Smartwatch": {
        "brands": {
            "Apple": ["Apple Watch Series 8", "Apple Watch Series 7", "Apple Watch SE", "Apple Watch Ultra", 
                      "Apple Watch Series 6", "Apple Watch 5", "Apple Watch 4", "Apple Watch 3", "Apple Watch 2", "Apple Watch 1"],
            "Samsung": ["Galaxy Watch 5 Pro", "Galaxy Watch 5", "Galaxy Watch 4 Classic", "Galaxy Watch 4", 
                        "Galaxy Watch 3", "Galaxy Watch Active 2", "Galaxy Watch Active", "Gear S3", "Gear Sport", "Gear Fit 2"],
            "Xiaomi": ["Mi Watch S1", "Mi Watch S1 Active", "Mi Watch", "Mi Watch Lite", "Mi Band 7", "Mi Band 7 Pro", 
                       "Mi Band 6", "Mi Band 5", "Mi Band 4", "Mi Band 3"],
            "Realme": ["Realme Watch 3 Pro", "Realme Watch 3", "Realme Watch 2 Pro", "Realme Watch 2", "Realme Band", 
                       "Realme Watch S Pro", "Realme Watch S", "Realme Watch", "Realme Band 2", "Realme Watch Pro"],
            "Noise": ["Noise ColorFit Pro 4", "Noise ColorFit Ultra", "Noise NoiseFit Evolve", "Noise NoiseFit Force", 
                      "Noise NoiseFit Active", "Noise Pulse", "Noise NoiseFit", "Noise NoiseBands", "Noise NoiseTone", "Noise NoiseCore"],
            "boAt": ["boAt Storm Pro", "boAt Storm", "boAt Wave Call", "boAt Wave", "boAt Lunar", "boAt Cosmos Pro", 
                     "boAt Cosmos", "boAt Xtend", "boAt Callisto", "boAt Blaze"],
            "Fastrack": ["Fastrack Reflex Vox", "Fastrack Reflex", "Fastrack Limitless", "Fastrack Smart Watch", 
                         "Fastrack Reflex Curv", "Fastrack Revoltt", "Fastrack Reflex Smartwatch", "Fastrack Reflex Active", "Fastrack Reflex", "Fastrack Reflex Smart"],
            "Garmin": ["Garmin Epix", "Garmin Fenix 7X", "Garmin Fenix 7", "Garmin Fenix 6X", "Garmin Epix Gen 2", 
                       "Garmin Vivoactive 4", "Garmin Vivoactive 3", "Garmin Venu", "Garmin Instinct", "Garmin Approach"],
        },
        "price_range": (2000, 60000),
        "rating_base": 4.0,
    },
    "Headphones": {
        "brands": {
            "Sony": ["Sony WH-1000XM5", "Sony WH-1000XM4", "Sony WH-1000XM3", "Sony WH-XB910N", "Sony WF-1000XM5", 
                     "Sony WF-1000XM4", "Sony WH-CH720N", "Sony WH-CH710N", "Sony WH-CH720", "Sony WH-XB700"],
            "JBL": ["JBL Tour Pro 2", "JBL Tour Pro", "JBL Live Pro 2", "JBL Live Pro", "JBL Flip 6", "JBL Flip 5", 
                    "JBL Charge 5", "JBL PartyBox", "JBL Authentics", "JBL Quantum"],
            "Bose": ["Bose QuietComfort 45", "Bose QuietComfort 35 II", "Bose Sport Earbuds", "Bose SoundLink Max", 
                     "Bose QuietComfort Ultra", "Bose Noise Cancelling Earbuds", "Bose SoundLink Revolve", "Bose SoundLink Mini", "Bose SoundLink Flex", "Bose SoundSport"],
            "Beats": ["Beats Studio Pro", "Beats Studio3", "Beats Solo4", "Beats Solo Pro", "Beats Fit Pro", 
                      "Beats Flex", "Beats PowerBeats Pro", "Beats Pro", "Beats Studio", "Beats Solo3"],
            "Sennheiser": ["Sennheiser Momentum 4", "Sennheiser Momentum 3", "Sennheiser Momentum True Wireless 3", 
                           "Sennheiser Momentum True Wireless 2", "Sennheiser HD 660S", "Sennheiser HD 650", "Sennheiser HD 599", "Sennheiser IE 200", "Sennheiser IE 100 Pro", "Sennheiser IE 80S"],
            "Audio-Technica": ["Audio-Technica ATH-M50x", "Audio-Technica ATH-M50xBT", "Audio-Technica ATH-SR50BT", 
                               "Audio-Technica ATH-WS1100", "Audio-Technica ATH-ANC500BT", "Audio-Technica ATH-ANC700BT", "Audio-Technica ATH-ANC9", "Audio-Technica ATH-AR3BT", "Audio-Technica ATH-AR5BT", "Audio-Technica ATH-MSR7NC"],
            "boAt": ["boAt Nirvanaa Pro", "boAt Airdopes 441", "boAt Airdopes 121v2", "boAt Rockerz 551", "boAt Rockerz 331", 
                     "boAt Rockerz 510", "boAt Rockerz 450", "boAt Bassheads 900", "boAt Rockerz 255", "boAt Bassheads 100"],
            "Noise": ["Noise Buds VS104", "Noise Buds VS102", "Noise Buds Pro 2", "Noise Buds Pro", "Noise Buds A1", 
                      "Noise Buds Pro 2.0", "Noise Buds VS101", "Noise Buds Pro 3", "Noise Buds Max", "Noise Buds Joy"],
            "OnePlus": ["OnePlus Buds Pro 2", "OnePlus Buds Pro", "OnePlus Buds Z2", "OnePlus Buds Z", "OnePlus Buds Nord", 
                        "OnePlus Buds", "OnePlus Pods", "OnePlus Bullets", "OnePlus Bullets Wireless Z2", "OnePlus Bullets Wireless Z"],
            "Samsung": ["Samsung Galaxy Buds2 Pro", "Samsung Galaxy Buds2", "Samsung Galaxy Buds Pro", "Samsung Galaxy Buds", 
                        "Samsung Galaxy Buds+", "Samsung Galaxy Buds Live", "Samsung Galaxy Fit2 Pro", "Samsung Galaxy Fit2", "Samsung Galaxy Fit Pro", "Samsung Galaxy Fit"],
        },
        "price_range": (1000, 40000),
        "rating_base": 4.1,
    },
    "Television": {
        "brands": {
            "Samsung": ["Samsung QN90B", "Samsung QN85B", "Samsung Q80B", "Samsung Q70B", "Samsung AU9000", 
                        "Samsung Crystal UHD", "Samsung OLED", "Samsung MicroLED", "Samsung The Wall", "Samsung Curved"],
            "LG": ["LG OLED55C3PUA", "LG OLED65C3PUA", "LG QNED86", "LG QNED85", "LG NanoCell", "LG OLED evo", 
                   "LG UltraSlim", "LG NanoCell QNED", "LG CineBeam", "LG OLED M3"],
            "Sony": ["Sony X95L", "Sony X93L", "Sony X90L", "Sony X80L", "Sony K-XR80", "Sony Bravia", 
                     "Sony Master Series", "Sony 8K", "Sony OLED", "Sony Mini LED"],
            "OnePlus": ["OnePlus TV 65 U1S", "OnePlus TV 55 U1S", "OnePlus TV 32", "OnePlus TV Y1S", "OnePlus TV Y1", 
                        "OnePlus TV U1S Pro", "OnePlus TV U1", "OnePlus TV U1S", "OnePlus TV 43", "OnePlus TV 55"],
            "Xiaomi": ["Xiaomi Mi TV 7", "Xiaomi Mi TV 6", "Xiaomi Mi TV 5", "Xiaomi RedmiTV Pro", "Xiaomi Mi TV P1", 
                       "Xiaomi Mi TV 4S", "Xiaomi Mi TV 4A", "Xiaomi Mi TV 4", "Xiaomi Mi TV 3S", "Xiaomi Mi TV 3"],
            "TCL": ["TCL C935", "TCL C835", "TCL P735", "TCL P635", "TCL S635", "TCL S535", "TCL P6", 
                    "TCL P5", "TCL P4", "TCL C1"],
            "Panasonic": ["Panasonic HX900", "Panasonic HX700", "Panasonic HX750", "Panasonic LX800", "Panasonic LX700", 
                          "Panasonic W95", "Panasonic W85", "Panasonic J95", "Panasonic J75", "Panasonic J95N"],
            "Hisense": ["Hisense U7H", "Hisense U6H", "Hisense U8H", "Hisense A6H", "Hisense A6G", 
                        "Hisense H8F", "Hisense H8G", "Hisense H9F", "Hisense H65", "Hisense H55"],
            "BPL": ["BPL 55 Smart TV", "BPL 43 Smart TV", "BPL 32 Smart TV", "BPL Nxtgen", "BPL Ultima", 
                    "BPL BPL55U4K", "BPL BPL43U4K", "BPL BPL55F", "BPL BPL43F", "BPL BPL32F"],
            "Kodak": ["Kodak 55", "Kodak 43", "Kodak 32", "Kodak 7X Pro", "Kodak 7X", 
                      "Kodak 9X Pro", "Kodak 9X", "Kodak UHD", "Kodak QLED", "Kodak Smart TV"],
        },
        "price_range": (15000, 500000),
        "rating_base": 4.2,
    },
    "Laptop": {
        "brands": {
            "Apple": ["MacBook Pro 16", "MacBook Pro 14", "MacBook Air M2", "MacBook Air M1", "MacBook Pro 13", 
                      "MacBook Air", "MacBook", "iMac 24", "Mac mini", "Mac Studio"],
            "Dell": ["Dell XPS 17", "Dell XPS 15", "Dell XPS 13", "Dell Inspiron", "Dell Vostro", 
                     "Dell Alienware", "Dell G15", "Dell G3", "Dell Latitude", "Dell Precision"],
            "HP": ["HP Spectre x360", "HP Pavilion", "HP Envy", "HP Elite", "HP ProBook", 
                   "HP Omen", "HP ProDesk", "HP Stream", "HP 15", "HP 14"],
            "Lenovo": ["Lenovo ThinkPad X1", "Lenovo ThinkPad E", "Lenovo Legion Y", "Lenovo IdeaPad", 
                       "Lenovo Yoga", "Lenovo ThinkBook", "Lenovo ProBook", "Lenovo Chromebook", "Lenovo ThinkPad", "Lenovo Tab P"],
            "ASUS": ["ASUS VivoBook", "ASUS ROG", "ASUS TUF Gaming", "ASUS ZenBook", "ASUS ProArt", 
                     "ASUS Chromebook", "ASUS ExpertBook", "ASUS Vivobook S", "ASUS M16", "ASUS N13"],
            "Acer": ["Acer Predator", "Acer Aspire", "Acer Swift", "Acer Nitro", "Acer TravelMate", 
                     "Acer Chromebook", "Acer ConceptD", "Acer Extensa", "Acer Spin", "Acer One"],
            "MSI": ["MSI Raider", "MSI Stealth", "MSI Creator", "MSI GE", "MSI GL", 
                    "MSI GS", "MSI GF", "MSI Pulse", "MSI Bravo", "MSI Modern"],
            "Asus": ["ASUS VivoBook F15", "ASUS VivoBook 15", "ASUS TUF Gaming", "ASUS ZenBook 14", "ASUS Chromebook Plus"],
        },
        "price_range": (20000, 500000),
        "rating_base": 4.3,
    },
    "Tablet": {
        "brands": {
            "Apple": ["iPad Pro 12.9", "iPad Pro 11", "iPad Air", "iPad", "iPad mini", 
                      "iPad 10th Gen", "iPad 9th Gen", "iPad 8th Gen", "iPad Air 5", "iPad Air 4"],
            "Samsung": ["Samsung Galaxy Tab S9", "Samsung Galaxy Tab S8", "Samsung Galaxy Tab A8", "Samsung Galaxy Tab A9", 
                        "Samsung Galaxy Tab S7", "Samsung Galaxy Tab M10", "Samsung Galaxy Tab S6", "Samsung Galaxy Tab A7", "Samsung Galaxy Tab S5e", "Samsung Galaxy Tab A"],
            "Xiaomi": ["Xiaomi Pad 5 Pro", "Xiaomi Pad 5", "Xiaomi Pad 4", "Xiaomi Mi Pad 5", "Xiaomi Redmi Pad", 
                       "Xiaomi Mi Pad", "Xiaomi Pad 6", "Xiaomi Pad 6 Pro", "Xiaomi Pad Ultra", "Xiaomi Mi Pad Air"],
            "OnePlus": ["OnePlus Pad", "OnePlus Tab", "OnePlus Pad Pro", "OnePlus Pad Air", "OnePlus Tab Air"],
            "Lenovo": ["Lenovo Tab P11 Pro", "Lenovo Tab M10", "Lenovo Tab P11", "Lenovo Tab A", 
                       "Lenovo Tab M8", "Lenovo Tab E", "Lenovo Tab P12 Pro", "Lenovo Tab P12", "Lenovo Tab M11", "Lenovo Tab A"],
            "Microsoft": ["Microsoft Surface Pro 9", "Microsoft Surface Pro 8", "Microsoft Surface Pro X", 
                          "Microsoft Surface Pro 7", "Microsoft Surface Go 3", "Microsoft Surface Go 2", "Microsoft Surface Laptop Go", "Microsoft Surface Laptop", "Microsoft Surface Book", "Microsoft Surface Duo"],
        },
        "price_range": (10000, 150000),
        "rating_base": 4.0,
    },
    "Camera": {
        "brands": {
            "Canon": ["Canon EOS R6", "Canon EOS R5", "Canon EOS R3", "Canon EOS M50", "Canon PowerShot", 
                      "Canon EOS 90D", "Canon EOS 80D", "Canon G7X", "Canon G5X", "Canon SX740"],
            "Nikon": ["Nikon Z9", "Nikon Z8", "Nikon Z6 III", "Nikon Z6 II", "Nikon Z5", 
                      "Nikon D850", "Nikon D780", "Nikon D500", "Nikon Z30", "Nikon Z50 II"],
            "Sony": ["Sony A7R V", "Sony A7 IV", "Sony A7S III", "Sony A6700", "Sony A6400", 
                     "Sony RX100 VII", "Sony RX100 VI", "Sony ZV-1", "Sony ZV-E10", "Sony A6100"],
            "Fujifilm": ["Fujifilm X-H2S", "Fujifilm X-T5", "Fujifilm X-H2", "Fujifilm X-T4", "Fujifilm X100V", 
                         "Fujifilm X-S20", "Fujifilm X-S10", "Fujifilm X-E4", "Fujifilm X-Pro3", "Fujifilm X-A7"],
            "Panasonic": ["Panasonic Lumix S1R", "Panasonic Lumix S1", "Panasonic Lumix GH6", "Panasonic Lumix GH5S", 
                          "Panasonic Lumix FZ1000", "Panasonic Lumix TZ100", "Panasonic Lumix LX100", "Panasonic Lumix S1H", "Panasonic Lumix GH5", "Panasonic Lumix G100"],
            "GoPro": ["GoPro Hero 11", "GoPro Hero 10", "GoPro Hero 9", "GoPro Max", "GoPro Fusion", 
                      "GoPro Hero 8", "GoPro Hero 7", "GoPro Hero 6", "GoPro Hero 5", "GoPro Session"],
        },
        "price_range": (20000, 800000),
        "rating_base": 4.4,
    },
    "Speaker": {
        "brands": {
            "JBL": ["JBL PartyBox 1100", "JBL PartyBox 320", "JBL PartyBox 110", "JBL Authentics 500", "JBL Flip 6", 
                    "JBL Charge 5", "JBL Boombox 2", "JBL Xtreme 3", "JBL Clip 4", "JBL Go 3"],
            "Sony": ["Sony SRS-XB100", "Sony SRS-XB23", "Sony SRS-XB33", "Sony SRS-XB43", "Sony SRS-UB60", 
                     "Sony SRS-RA5000", "Sony SRS-NS7", "Sony SRS-XG500", "Sony SRS-XE300", "Sony SRS-XP900"],
            "Bose": ["Bose SoundLink Revolve+", "Bose SoundLink Revolve", "Bose SoundLink Flex", "Bose SoundLink Mini", 
                     "Bose SoundLink Max", "Bose Home", "Bose Smart Ultra", "Bose Smart", "Bose Portable", "Bose Solo"],
            "Beats": ["Beats Pill", "Beats Beatbox", "Beats Studio Pro Speaker"],
            "Ultimate Ears": ["Ultimate Ears BOOM 3", "Ultimate Ears MEGABOOM 3", "Ultimate Ears WONDERBOOM", 
                              "Ultimate Ears HYPERBOOM", "Ultimate Ears BOOM 2", "Ultimate Ears MEGABOOM 2"],
            "boAt": ["boAt Stone 1100", "boAt Stone 650B", "boAt Stone 1100F", "boAt Aavante 1000", "boAt Aavante 815", 
                     "boAt Aavante 415", "boAt Aavante 1200", "boAt Aavante 615", "boAt Aavante 215", "boAt Xtreme 2"],
            "Noise": ["Noise Vortex Max", "Noise Vortex", "Noise Hush Charge", "Noise Hush", "Noise Speaker Max"],
        },
        "price_range": (2000, 150000),
        "rating_base": 4.1,
    },
    "Gaming Console": {
        "brands": {
            "Sony": ["PlayStation 5", "PlayStation 5 Digital", "PlayStation 4 Pro", "PlayStation 4", "PSVita"],
            "Microsoft": ["Xbox Series X", "Xbox Series S", "Xbox One X", "Xbox One S", "Xbox One"],
            "Nintendo": ["Nintendo Switch OLED", "Nintendo Switch", "Nintendo Switch Lite", "Nintendo 3DS XL", "Nintendo 2DS XL"],
        },
        "price_range": (15000, 80000),
        "rating_base": 4.5,
    },
    "Drone": {
        "brands": {
            "DJI": ["DJI Air 3S", "DJI Air 3", "DJI Mini 3 Pro", "DJI Mini 3", "DJI Mini 2SE", 
                    "DJI Mini 2", "DJI Mavic 3", "DJI Mavic 3 Classic", "DJI Avata", "DJI FPV"],
            "Parrot": ["Parrot Anafi Extended", "Parrot Anafi", "Parrot Bebop 2", "Parrot Bebop 2 FPV"],
        },
        "price_range": (25000, 500000),
        "rating_base": 4.3,
    },
    # Home & Kitchen Appliances added per user request
    "Refrigerator": {
        "brands": {
            "LG": ["LG Frost Free 260L", "LG Frost Free 300L", "LG Inverter 335L"],
            "Samsung": ["Samsung RT28", "Samsung 322L", "Samsung Frost Free 450L"],
            "Whirlpool": ["Whirlpool 190L", "Whirlpool 265L", "Whirlpool 340L"]
        },
        "price_range": (15000, 120000),
        "rating_base": 4.0,
    },
    "Washing Machine": {
        "brands": {
            "LG": ["LG Front Load 7kg", "LG Top Load 8kg", "LG Inverter 6kg"],
            "Samsung": ["Samsung Twin Tub", "Samsung Front Load 7kg", "Samsung Top Load 9kg"],
            "IFB": ["IFB Front Load 6kg", "IFB Top Load 8kg"]
        },
        "price_range": (8000, 70000),
        "rating_base": 4.0,
    },
    "Microwave Oven": {
        "brands": {
            "Panasonic": ["Panasonic NN-ST34", "Panasonic NN-CT65"],
            "LG": ["LG Convection 28L", "LG Solo 20L"],
            "IFB": ["IFB 20SC4", "IFB 25SC6"]
        },
        "price_range": (4000, 35000),
        "rating_base": 4.0,
    },
    "Air Conditioner": {
        "brands": {
            "Voltas": ["Voltas 1.5 Ton", "Voltas 2 Ton"],
            "LG": ["LG Dual Inverter 1.5 Ton", "LG 1 Ton"],
            "Samsung": ["Samsung AR18", "Samsung AR24"]
        },
        "price_range": (25000, 150000),
        "rating_base": 4.0,
    },
    "Electric Fan": {
        "brands": {
            "Crompton": ["Crompton 1200mm", "Crompton 900mm"],
            "Havells": ["Havells 1200mm", "Havells 900mm"],
            "Usha": ["Usha 1200mm", "Usha 900mm"]
        },
        "price_range": (800, 6000),
        "rating_base": 4.1,
    },
    "Geyser": {
        "brands": {
            "Bajaj": ["Bajaj New Shakti 25L", "Bajaj Calenta 15L"],
            "AO Smith": ["AO Smith 25L", "AO Smith 15L"],
            "Havells": ["Havells 15L", "Havells 25L"]
        },
        "price_range": (3000, 20000),
        "rating_base": 4.0,
    },
    "Mixer Grinder": {
        "brands": {
            "Philips": ["Philips HL7756", "Philips HL7707", "Philips HL Series"],
            "Sujata": ["Sujata Dynamix", "Sujata Powermatic"],
            "Bajaj": ["Bajaj GX1", "Bajaj Rex"],
            "Preethi": ["Preethi Zodiac", "Preethi Blue Leaf", "Preethi Eco Plus", "Preethi Chef Pro", "Preethi Steele", "Preethi Lavender"],
            "Butterfly": ["Butterfly Jet Elite", "Butterfly Matchless"],
            "Havells": ["Havells Sprint", "Havells Momenta"],
            "Prestige": ["Prestige Iris", "Prestige Nakshatra"]
        },
        "price_range": (800, 12000),
        "rating_base": 4.1,
    },

    "Clothing": {
        "brands": {
            "Various": [
                "Kanchipuram Silk (Pure silk saree)",
                "Madisar Saree (9-yard saree)",
                "Cotton Saree",
                "Chettinad Cotton",
                "Sungudi Cotton",
                "Pavadai Sattai (Skirt & blouse material)",
                "Half Saree / Langa Voni",
                "Raw Silk Material",
                "Art Silk (Synthetic silk)",
                "Veshti (Dhoti) Cotton",
                "Silk Veshti",
                "Angavastram Cotton/Silk",
                "Mundu Material",
                "Chudi",
                "T-Shirt",
                "Hoodie",
                "Shirt",
                "Pant"
            ]
        },
        "price_range": (200, 50000),
        "rating_base": 4.0,
    },
    "Electric Iron": {
        "brands": {
            "Philips": ["Philips Steam Iron 1440W", "Philips Dry Iron 1100W"],
            "Bajaj": ["Bajaj DX4", "Bajaj Majesty"],
            "Morphy Richards": ["Morphy Richards 1000W"]
        },
        "price_range": (500, 3000),
        "rating_base": 4.2,
    },
    "Vacuum Cleaner": {
        "brands": {
            "Kirby": ["Kirby Sentria", "Kirby Avalir"],
            "Philips": ["Philips PowerPro", "Philips Performer"],
            "Eureka": ["Eureka Forbes Quick Clean", "Eureka Forbes Trendy"]
        },
        "price_range": (2000, 45000),
        "rating_base": 4.0,
    },
    "Induction Cooktop": {
        "brands": {
            "Prestige": ["Prestige PIC 20", "Prestige Induction 371"],
            "Philips": ["Philips Viva Collection"],
            "Bajaj": ["Bajaj Majesty ICX" ]
        },
        "price_range": (800, 6000),
        "rating_base": 4.1,
    },
    "Gas Stove": {
        "brands": {
            "Prestige": ["Prestige Marvel Plus", "Prestige Royale Plus"],
            "Hindware": ["Hindware Gas Stove 2 Burner", "Hindware Gas Stove 3 Burner"],
            "Sunflame": ["Sunflame GT Pride", "Sunflame Gas Stove"]
        },
        "price_range": (1200, 8000),
        "rating_base": 4.0,
    },
    "Rice Cooker": {
        "brands": {
            "Philips": ["Philips Daily Collection", "Philips Viva"],
            "Panasonic": ["Panasonic SR-TR"],
            "Prestige": ["Prestige Nakshatra", "Prestige Deluxe"]
        },
        "price_range": (800, 6000),
        "rating_base": 4.1,
    },
    "Toaster": {
        "brands": {
            "Philips": ["Philips Toaster HD2581"],
            "Bajaj": ["Bajaj Toaster 2 Slice"],
            "Morphy Richards": ["Morphy Richards Toaster"]
        },
        "price_range": (500, 4000),
        "rating_base": 4.2,
    },
    "Electric Kettle": {
        "brands": {
            "Borosil": ["Borosil Hotline 1.5L"],
            "Philips": ["Philips Electric Kettle 1.2L"],
            "Prestige": ["Prestige Kettle 1.8L"]
        },
        "price_range": (600, 4000),
        "rating_base": 4.2,
    },
    "Blender": {
        "brands": {
            "Philips": ["Philips HL7756 Blender", "Philips Daily Collection"],
            "Bajaj": ["Bajaj Stainless Steel Mixer"],
            "Preethi": ["Preethi Zodiac", "Preethi Blue Leaf"]
        },
        "price_range": (1200, 7000),
        "rating_base": 4.1,
    },
    "Dishwasher": {
        "brands": {
            "Bosch": ["Bosch 12 Place", "Bosch 14 Place"],
            "LG": ["LG Compact Dishwasher"],
            "IFB": ["IFB Neptune" ]
        },
        "price_range": (20000, 120000),
        "rating_base": 4.0,
    },
    "Water Purifier": {
        "brands": {
            "Kent": ["Kent Grand", "Kent Ultra"],
            "Aquaguard": ["Aquaguard Delight", "Aquaguard Enhance"],
            "Eureka Forbes": ["AquaSure", "Eureka Forbes Aquaguard"]
        },
        "price_range": (4000, 50000),
        "rating_base": 4.0,
    },
    "Room Heater": {
        "brands": {
            "Bajaj": ["Bajaj Room Heater 2000W", "Bajaj Room Heater 1500W"],
            "Orpat": ["Orpat Room Heater 2000W"],
            "Usha": ["Usha Room Heater 1500W"]
        },
        "price_range": (800, 8000),
        "rating_base": 4.1,
    },
    "Air Cooler": {
        "brands": {
            "Symphony": ["Symphony Siesta", "Symphony Diet"],
            "Bajaj": ["Bajaj Platini", "Bajaj DC"],
            "Havells": ["Havells Frost" ]
        },
        "price_range": (4000, 30000),
        "rating_base": 4.0,
    },
    "Jewellery": {
        "brands": {
            "Tanishq": [
                "Necklace - Classic Gold", "Chain - Gold", "Earrings - Studs", "Earrings - Jhumka", "Earrings - Drops",
                "Bangles - Gold", "Bracelet - Gold", "Ring - Gold", "Anklet - Payal", "Nose Pin - Gold", "Mangalsutra - Traditional"
            ],
            "Kalyan": [
                "Necklace - Temple", "Chain - Men Gold", "Kada - Heavy", "Ring - Diamond" 
            ],
            "Malabar": [
                "Bracelet - Designer", "Bangles - Bridal", "Anklet - Designer"
            ],
            "Various": [
                "Hair Accessory - Hair Clip", "Hair Chain - Decorative"
            ]
        },
        "price_range": (500, 200000),
        "rating_base": 4.3,
    },
    "Makeup": {
        "brands": {
            "Maybelline": ["Foundation", "Compact Powder", "Concealer", "Blush", "Highlighter"],
            "Lakme": ["Kajal", "Eyeliner", "Eyeshadow", "Mascara"],
            "MAC": ["Lipstick", "Lip Gloss", "Lip Liner"],
            "Nykaa": ["Nail Polish", "Nail Remover", "Makeup Brushes", "Beauty Blender"],
            "Various": ["Face Makeup Combo", "Eye Makeup Combo", "Lip Makeup Combo"]
        },
        "price_range": (100, 10000),
        "rating_base": 4.0,
    },
}

def generate_warranty():
    """Generate random warranty in years"""
    return random.choice([1, 2, 3, 5])

def generate_price(base_price_range):
    """Generate realistic product price"""
    base = random.uniform(base_price_range[0], base_price_range[1])
    # Add some variation
    variation = random.uniform(0.85, 1.15)
    return round(base * variation, -2)  # Round to nearest 100

def generate_rating(category):
    """Generate realistic product rating"""
    base = ELECTRONICS_CATALOG[category]["rating_base"]
    rating = random.gauss(base, 0.4)
    rating = max(1.0, min(5.0, rating))
    return round(rating, 1)

def generate_product_url(website_code, category, brand, model):
    """Generate realistic product URL"""
    product_name = f"{brand}-{model}".lower().replace(" ", "-")
    product_id = random.randint(1000000, 9999999)
    
    urls = {
        "amazon": f"https://amazon.in/s?k={product_name}",
        "flipkart": f"https://flipkart.com/{product_name}",
        "meesho": f"https://meesho.com/{product_name}",
        "myntra": f"https://myntra.com/{product_name}",
        "snapdeal": f"https://snapdeal.com/{product_name}",
        "reliancedigital": f"https://reliancedigital.in/products/{product_name}",
        "croma": f"https://croma.com/{product_name}",
    }
    return urls.get(website_code, f"https://example.com/{product_name}")

def generate_datasets():
    """Generate complete electronics dataset"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for website_name, website_code in WEBSITES:
        filename = os.path.join(OUTPUT_DIR, f"{website_code}_electronics_{NUM_PRODUCTS}_fullspecs.csv")
        
        print(f"Generating {website_name} dataset with {NUM_PRODUCTS} products...")
        
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "product_id",
                "product_name",
                "category",
                "brand",
                "model",
                "price",
                "rating",
                "warranty_years",
                "website",
                "product_link",
                "in_stock",
                "description"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            product_id = 1
            categories = list(ELECTRONICS_CATALOG.keys())
            
            # Generate products - distribute across categories and handle remainder so total == NUM_PRODUCTS
            products_per_category = NUM_PRODUCTS // len(categories)
            remainder = NUM_PRODUCTS - (products_per_category * len(categories))

            for idx, category in enumerate(categories):
                category_data = ELECTRONICS_CATALOG[category]
                brands_list = list(category_data["brands"].items())

                # Give one extra product to the first `remainder` categories
                count_for_category = products_per_category + (1 if idx < remainder else 0)

                for _ in range(count_for_category):
                    brand, models = random.choice(brands_list)
                    model = random.choice(models)

                    price = generate_price(category_data["price_range"])
                    rating = generate_rating(category)
                    warranty = generate_warranty()
                    in_stock = random.choice(["Yes", "No"])

                    product_name = f"{brand} {model}"
                    product_link = generate_product_url(website_code, category, brand, model)

                    description = f"{product_name} - Premium {category.lower()} with excellent features. Price: ₹{price:,}, Rating: {rating}/5"

                    writer.writerow({
                        "product_id": product_id,
                        "product_name": product_name,
                        "category": category,
                        "brand": brand,
                        "model": model,
                        "price": price,
                        "rating": rating,
                        "warranty_years": warranty,
                        "website": website_name,
                        "product_link": product_link,
                        "in_stock": in_stock,
                        "description": description
                    })

                    product_id += 1
        
        print(f"✓ Generated {filename}")
    
    print(f"\n✓ All datasets generated successfully!")
    print(f"✓ Each website has {NUM_PRODUCTS} electronic products")
    print(f"✓ Categories included: {', '.join(categories)}")
    print(f"✓ Attributes: Price, Rating, Warranty, Stock Status, Product Link")

if __name__ == "__main__":
    generate_datasets()
