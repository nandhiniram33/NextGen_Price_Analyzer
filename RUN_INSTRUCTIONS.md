# 🚀 HOW TO RUN THE PRICE COMPARISON APP

## Prerequisites
- Python 3.7 or higher installed
- Windows/Mac/Linux

## Step-by-Step Guide

### **Step 1: Open Command Prompt/Terminal**
Navigate to the project directory:
```bash
cd c:\Users\hp\Downloads\Price comparison (2)\Price comparison\Price comparison
```

### **Step 2: Install Dependencies**
Run this command to install Flask and Pandas:
```bash
python -m pip install flask pandas
```

Expected output:
```
Successfully installed flask-3.x.x pandas-2.x.x
```

### **Step 3: Start the Flask App**
Run the Flask application:
```bash
python app.py
```

Expected output:
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### **Step 4: Open in Web Browser**
Open your web browser and go to:
```
http://127.0.0.1:5000
```

Or click the link from the terminal output.

---

## ✅ App is Now Running!

You should see a search form on the page.

---

## 📝 How to Use the App

### Search for Products
1. Type in a product name in the search box
2. Examples:
   - `HP Pavilion` (specific laptop)
   - `Sony` (all Sony products)
   - `Smartphone` (all phones)
   - `Apple iPhone 14` (specific model)
   - `Samsung TV` (televisions)
   - `Dell` (all Dell products)
   - `Headphones` (all headphones)
   - `Drone` (all drones)

3. Click **Search** button

### View Results
The app will show:
- ✅ **Product Name** and **Brand**
- ✅ **7 Website Prices**:
  - Amazon
  - Flipkart
  - Meesho
  - Myntra
  - Snapdeal
  - RelianceDigital
  - Croma
- ✅ **Rating** from each website (1-5 stars)
- ✅ **Warranty** period in years
- ✅ **Direct Links** to products

---

## 📊 Database Information

### Total Products: **105,000**
- 15,000 products per website
- 10 product categories
- 1,500 products per category per website

### Categories Available:
1. Smartphones
2. Smartwatches
3. Headphones
4. Televisions
5. Laptops
6. Tablets
7. Cameras
8. Speakers
9. Gaming Consoles
10. Drones

### Brands Included:
- **Smartphones**: Apple, Samsung, Xiaomi, OnePlus, Realme, OPPO, Vivo, Motorola
- **Smartwatches**: Apple Watch, Samsung, Xiaomi, Noise, boAt, Fastrack, Garmin
- **Headphones**: Sony, JBL, Bose, Beats, Sennheiser, Audio-Technica, boAt
- **TV**: Samsung, LG, Sony, OnePlus, Xiaomi, TCL, Panasonic, Hisense, BPL, Kodak
- **Laptops**: Apple, Dell, HP, Lenovo, ASUS, Acer, MSI
- **Tablets**: Apple, Samsung, Microsoft, Lenovo, Xiaomi, OnePlus
- **Cameras**: Canon, Nikon, Sony, Fujifilm, Panasonic, GoPro
- **Speakers**: JBL, Sony, Bose, Ultimate Ears, boAt, Noise
- **Gaming**: PlayStation, Xbox, Nintendo
- **Drones**: DJI, Parrot

---

## 🛑 To Stop the App

Press `CTRL+C` in the terminal where the app is running:
```
Press CTRL+C to quit
```

---

## ⚠️ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Run `python -m pip install flask pandas`

### Problem: "Port 5000 already in use"
**Solution**: 
1. Stop any other Flask apps running
2. Or restart your computer
3. Or change port in app.py (last line): `app.run(debug=True, port=5001)`

### Problem: "No search results"
**Solution**: 
- Try different search terms
- Search by brand name (e.g., "Sony", "Apple")
- Search by category (e.g., "smartphone", "laptop")
- Try partial names (e.g., "iPhone" instead of full model)

### Problem: App not responding after search
**Solution**:
- Reload the page (F5 or Ctrl+R)
- Close browser and reopen http://127.0.0.1:5000
- Restart the Flask app

---

## 📁 Project Files

```
Price comparison/
├── app.py (Main Flask application)
├── requirements.txt (Dependencies)
├── generate_electronics_datasets.py (Data generator)
├── test_search.py (Search test script)
├── dataset/ (CSV files with 15,000 products each)
│   ├── amazon_electronics_15000_fullspecs.csv
│   ├── flipkart_electronics_15000_fullspecs.csv
│   ├── meesho_electronics_15000_fullspecs.csv
│   ├── myntra_electronics_15000_fullspecs.csv
│   ├── snapdeal_electronics_15000_fullspecs.csv
│   ├── reliancedigital_electronics_15000_fullspecs.csv
│   └── croma_electronics_15000_fullspecs.csv
├── templates/
│   └── index.html (Web interface)
├── static/
│   └── style.css (Styling)
└── README files
```

---

## 🎯 Quick Start (3 Simple Steps)

### Windows PowerShell/CMD:
```bash
cd c:\Users\hp\Downloads\Price comparison (2)\Price comparison\Price comparison
python -m pip install flask pandas
python app.py
```

### Then open:
```
http://127.0.0.1:5000
```

Done! ✅

---

## 💡 Features

✨ **Instant Price Comparison**
- Compare same product across 7 websites
- See all prices, ratings, warranty at once

✨ **Advanced Search**
- Search by product name
- Search by brand
- Search by category
- Partial text matching

✨ **Real Data**
- 105,000 electronics products
- Realistic pricing
- Natural ratings (1-5 stars)
- Warranty information
- Stock status

✨ **7 Major E-commerce Websites**
- Amazon
- Flipkart
- Meesho
- Myntra
- Snapdeal
- RelianceDigital
- Croma

---

## 🔗 Useful Links

**Local URL:** http://127.0.0.1:5000

**Documentation:** Check ELECTRONICS_DATASET_SUMMARY.md for complete dataset info

**Search Examples:** Check SEARCH_FIXED.md for search tips

---

## 📞 Support

If you encounter any issues:
1. Check Troubleshooting section above
2. Ensure all dependencies are installed
3. Make sure Flask is running (check terminal output)
4. Verify browser is accessing http://127.0.0.1:5000

---

**Enjoy your Price Comparison App!** 🎉
