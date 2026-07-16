"""
Generates a realistic synthetic retail sales SQLite database with
customers, products, and orders tables (normalized, with foreign keys),
for practicing SQL joins, aggregations, and window functions.
"""
import sqlite3
import numpy as np
import pandas as pd
from datetime import date, timedelta

rng = np.random.default_rng(7)
conn = sqlite3.connect("retail_sales.db")
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    region TEXT,
    signup_date TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    unit_price REAL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    order_date TEXT,
    quantity INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
""")

# --- Customers ---
regions = ['North', 'South', 'East', 'West']
n_customers = 150
start = date(2023, 1, 1)
customers = []
for cid in range(1, n_customers + 1):
    signup = start + timedelta(days=int(rng.integers(0, 700)))
    customers.append((cid, f"Customer_{cid}", rng.choice(regions), signup.isoformat()))
cur.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)

# --- Products ---
categories = {
    'Electronics': [('Wireless Mouse', 15.99), ('Bluetooth Speaker', 39.99), ('USB-C Hub', 24.99), ('Laptop Stand', 29.99)],
    'Apparel': [('Cotton T-Shirt', 12.99), ('Denim Jacket', 59.99), ('Running Shoes', 74.99)],
    'Home': [('Ceramic Mug', 8.99), ('Table Lamp', 34.99), ('Throw Blanket', 22.99)],
    'Grocery': [('Coffee Beans 1kg', 14.99), ('Olive Oil 500ml', 9.99), ('Almonds 500g', 7.99)],
}
products = []
pid = 1
for cat, items in categories.items():
    for name, price in items:
        products.append((pid, name, cat, price))
        pid += 1
cur.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

# --- Orders (with mild seasonality: more orders Nov-Dec) ---
n_orders = 4000
orders = []
for oid in range(1, n_orders + 1):
    cust_id = int(rng.integers(1, n_customers + 1))
    prod_id = int(rng.integers(1, len(products) + 1))
    day_offset = int(rng.integers(0, 730))
    order_date = start + timedelta(days=day_offset)
    # Boost quantity slightly in Nov/Dec to simulate a holiday bump
    boost = 2 if order_date.month in (11, 12) else 0
    qty = int(rng.integers(1, 5)) + (rng.integers(0, boost + 1) if boost else 0)
    orders.append((oid, cust_id, prod_id, order_date.isoformat(), qty))
cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)

conn.commit()
conn.close()
print(f"Created retail_sales.db with {n_customers} customers, {len(products)} products, {n_orders} orders")
