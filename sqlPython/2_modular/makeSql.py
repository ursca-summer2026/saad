import sqlite3
import random

with open('schema.sql', 'r') as f:
    schema_script = f.read()

databaseFile = 'database.db'

with sqlite3.connect(databaseFile) as conn:
    conn.executescript(schema_script) # Runs multiple SQL statements at once
    
# Add some random sample data
sample_products = [
    'Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones',
    'Webcam', 'Speaker', 'Tablet', 'Printer', 'Router',
    'USB Cable', 'HDMI Cable', 'Phone Charger', 'Desk Lamp', 'Notebook'
]

# Insert random products
for product_name in sample_products:
    price = round(random.uniform(9.99, 999.99), 2)
    conn.execute('INSERT INTO products (name, price) VALUES (?, ?)', (product_name, price))

conn.commit()
print(f"Database schema created successfully: {databaseFile}.")
print(f"Added {len(sample_products)} random products to the database.")

