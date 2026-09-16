import os
import random
import csv
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from database.db import init_db, get_db

def seed():
    # 1. Init DB
    init_db()
    conn = get_db()
    cur = conn.cursor()

    # 2. Insert admin
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                ('Admin', 'admin@nearshop.com', generate_password_hash('admin123'), 'owner'))
    admin_id = cur.lastrowid

    # 3. Insert customer
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                ('Test Customer', 'customer@nearshop.com', generate_password_hash('cust123'), 'customer'))
    customer_id = cur.lastrowid

    # 4. Insert 50 shops
    shop_names = ['Srinivas Auto Parts', 'Lakshmi Hardware', 'Venkateshwara Electricals', 'Maruti Spares', 'Sri Ram Traders', 'Ganesh General Store', 'Om Sai Plumbing', 'Balaji Garments', 'Saraswati Books', 'Durga Footwear']
    categories = ['Vehicle Spare Parts', 'Electrical', 'Hardware', 'Footwear', 'Stationery', 'Books', 'Garments', 'Plumbing', 'General Store']
    
    shops = []
    for i in range(50):
        name = random.choice(shop_names) + f" {i+1}"
        cat = random.choice(categories)
        lat = random.uniform(15.13, 15.18)
        lng = random.uniform(76.90, 76.96)
        cur.execute("INSERT INTO shops (owner_id, shop_name, category, address, latitude, longitude, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (admin_id, name, cat, f'Street {i+1}, Ballari', lat, lng, '9876543210'))
        shops.append((cur.lastrowid, cat))

    # 5. Read products.csv and insert 20 per shop
    products_csv = os.path.join(os.path.dirname(__file__), 'dataset', 'products.csv')
    all_products = []
    with open(products_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_products.append(row)

    product_ids = []
    for shop_id, shop_cat in shops:
        # Filter products matching shop category or pick random
        shop_prods = [p for p in all_products if p['category'] == shop_cat]
        if not shop_prods:
            shop_prods = all_products
            
        selected = random.choices(shop_prods, k=20)
        for p in selected:
            price = float(p['price'])
            # vary price by +/- 15%
            price = price * random.uniform(0.85, 1.15)
            qty = random.randint(1, 200)
            cur.execute("""INSERT INTO products (shop_id, product_name, category, description, price, quantity, brand) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (shop_id, p['product_name'], p['category'], p['description'], round(price, 2), qty, p['brand']))
            product_ids.append(cur.lastrowid)

    # 6. Insert 200 search_history
    for _ in range(200):
        prod = random.choice(all_products)['product_name']
        days_ago = random.randint(0, 30)
        timestamp = datetime.now() - timedelta(days=days_ago)
        cur.execute("INSERT INTO search_history (customer_id, product_name, timestamp) VALUES (?, ?, ?)",
                    (customer_id, prod, timestamp))

    # 7. Insert price_history for all products for last 30 days
    for pid in product_ids:
        base_price = random.uniform(50, 2000)
        for days_ago in range(30):
            date = (datetime.now() - timedelta(days=days_ago)).date()
            p_price = base_price * random.uniform(0.9, 1.1)
            cur.execute("INSERT INTO price_history (product_id, price, date) VALUES (?, ?, ?)",
                        (pid, round(p_price, 2), date))

    conn.commit()
    conn.close()
    print("Database seeded successfully.")

    # 8 & 9. Call models (assuming they exist or will exist)
    try:
        from models import apriori
        apriori.train_model()
        print("Apriori model trained.")
    except Exception as e:
        print(f"Skipping Apriori training: {e}")

    try:
        from models import word2vec
        word2vec.train_model()
        print("Word2Vec model trained.")
    except Exception as e:
        print(f"Skipping Word2Vec training: {e}")

if __name__ == '__main__':
    seed()
