import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect("saf_printings.db")
cursor = conn.cursor()

# Create the products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )
''')

# Ensure the products table exists by checking its existence
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
if not cursor.fetchone():
    print("Error: 'products' table does not exist. Creating it now...")

    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')
    print("Products table created successfully.")

# Create the invoices table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        contact TEXT NOT NULL,
        address TEXT NOT NULL,
        total_price REAL NOT NULL
    )
''')

# Create the invoice items table (to store products for each invoice)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        discount REAL DEFAULT 0,
        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database initialized successfully.")
