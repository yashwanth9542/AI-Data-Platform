import sqlite3
from pathlib import Path

path = Path("backend/data/analytics.db")
path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(path)
cur = conn.cursor()
cur.executescript(
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        region TEXT,
        segment TEXT,
        signup_date TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        category TEXT,
        price REAL
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        order_date TEXT,
        quantity INTEGER,
        amount REAL,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );

    INSERT INTO customers (id, region, segment, signup_date) VALUES
        (1, 'North', 'Enterprise', '2024-01-10'),
        (2, 'West', 'SMB', '2024-02-18'),
        (3, 'South', 'Enterprise', '2024-03-22'),
        (4, 'East', 'SMB', '2024-04-05')
    ON CONFLICT(id) DO NOTHING;

    INSERT INTO products (id, category, price) VALUES
        (1, 'Analytics', 1200.0),
        (2, 'AI', 890.0),
        (3, 'Reporting', 560.0)
    ON CONFLICT(id) DO NOTHING;

    INSERT INTO orders (id, customer_id, product_id, order_date, quantity, amount) VALUES
        (1, 1, 1, '2024-05-01', 2, 2400.0),
        (2, 1, 2, '2024-05-07', 1, 890.0),
        (3, 2, 3, '2024-05-08', 3, 1680.0),
        (4, 3, 1, '2024-05-12', 1, 1200.0),
        (5, 4, 2, '2024-05-14', 2, 1780.0)
    ON CONFLICT(id) DO NOTHING;
    """
)
conn.commit()
print(path.resolve())
print(cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall())
print(cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0])
conn.close()
