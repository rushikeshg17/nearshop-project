# 🛍️ NearShop — AI-Based Hyperlocal Shop Inventory Discovery System

> Final-year Computer Science Project | Ballari, Karnataka, India

NearShop is a web application that helps customers in Ballari discover **which nearby shops have the product they need**, using AI-powered search, real-time inventory, and location-based filtering.

---

## ✨ Features

### For Customers
- 🔍 **AI-Powered Search** — Word2Vec semantic search finds products even with partial or alternate words
- 📍 **Location-Based Results** — Shows shops within 5 km radius, sorted by proximity
- 🏷️ **Category Browsing** — Quick browse by 8 product categories
- 💡 **Smart Recommendations** — Apriori-based "frequently bought together" suggestions
- 🗺️ **Live Shop Map** — Interactive Leaflet map showing all shops with matching inventory

### For Shop Owners
- 📦 **Catalog-Based Product Addition** — Add products from a curated catalog (no typing required)
- 📊 **Sales Dashboard** — Stock trends, category breakdown, top products, expiry alerts
- ✏️ **Quick Stock Update** — Click quantity to edit inline
- 🗺️ **Shop Registration with Map Pin** — Place your shop on the map with geolocation support

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite |
| ML Models | Word2Vec (Gensim), Apriori (mlxtend) |
| Maps | Leaflet.js + OpenStreetMap |
| Frontend | Bootstrap 5, Bootstrap Icons |
| Auth | Flask sessions |

---

## 📂 Project Structure

```
NearShop/
├── app.py                  # App factory, blueprint registration
├── config.py               # Configuration, categories, colors
├── database/
│   └── db.py               # SQLite connection, schema init
├── routes/
│   ├── auth.py             # Login, register, logout
│   ├── dashboard.py        # Owner dashboard, analytics API
│   ├── product.py          # Product CRUD, catalog, bulk add
│   └── search.py           # Search + recommendations
├── models/
│   ├── word2vec.py         # Semantic search model
│   └── apriori.py          # Association rules
├── templates/              # Jinja2 HTML templates
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/products/    # Product category images
└── dataset/
    └── products.csv        # Product catalog
```

---

## 🚀 Setup & Run

### 1. Clone & install dependencies
```bash
git clone https://github.com/YOUR_USERNAME/NearShop.git
cd NearShop
pip install -r requirements.txt
```

### 2. Initialize database & seed data
```bash
python3 seed_data.py
```

### 3. Train ML models
```bash
python3 -c "from models.word2vec import train_model; train_model()"
```

### 4. Run the app
```bash
python3 -c "from app import app; app.run(debug=True, host='0.0.0.0', port=5001)"
```

Open [http://localhost:5001](http://localhost:5001)

---

## 👤 Demo Accounts

| Role | Email | Password |
|---|---|---|
| Admin / Owner | `admin@nearshop.com` | `admin123` |
| Customer | `customer@nearshop.com` | `cust123` |

---

## 🏪 Categories Supported

- 🔧 Vehicle Spare Parts
- ⚡ Electrical
- 🔨 Hardware
- 🚰 Plumbing
- 👟 Footwear
- ✏️ Stationery
- 📚 Books
- 🏪 General Store

---

## 📍 Location

Designed for **Ballari (Bellary), Karnataka, India**  
Default map center: `15.1394°N, 76.9214°E`

---

## 📸 Screenshots

> *(Add screenshots here)*

---

## 📄 License

MIT License — Free for educational use.
