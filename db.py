# db.py
import sqlite3

conn = sqlite3.connect("roshen_orders.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_name TEXT,
    quantity INTEGER
)
""")
conn.commit()

def add_order(user_id: int, product_name: str, quantity: int):
    cursor.execute("INSERT INTO orders (user_id, product_name, quantity) VALUES (?, ?, ?)",
                   (user_id, product_name, quantity))
    conn.commit()

def get_orders_by_user(user_id: int):
    cursor.execute("SELECT product_name, quantity FROM orders WHERE user_id = ?", (user_id,))
    return cursor.fetchall()
