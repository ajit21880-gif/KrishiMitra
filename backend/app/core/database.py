import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATABASE_PATH = os.path.join(BASE_DIR, "krishimitra.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        mobile TEXT UNIQUE,
        preferred_language TEXT DEFAULT 'en',
        state TEXT,
        district TEXT,
        village TEXT,
        created_at TEXT
    )
    """)
    
    # Create mandis table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mandis (
        id TEXT PRIMARY KEY,
        state TEXT,
        district TEXT,
        mandi_name TEXT,
        apmc_code TEXT UNIQUE,
        latitude REAL,
        longitude REAL
    )
    """)
    
    # Create commodities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS commodities (
        id TEXT PRIMARY KEY,
        commodity_name TEXT,
        local_name TEXT,
        category TEXT
    )
    """)
    
    # Create daily_prices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_prices (
        id TEXT PRIMARY KEY,
        mandi_id TEXT,
        commodity_id TEXT,
        date TEXT,
        min_price REAL,
        modal_price REAL,
        max_price REAL,
        source TEXT DEFAULT 'AGMARKNET',
        FOREIGN KEY (mandi_id) REFERENCES mandis (id),
        FOREIGN KEY (commodity_id) REFERENCES commodities (id)
    )
    """)
    
    # Create buyers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buyers (
        id TEXT PRIMARY KEY,
        company TEXT,
        gst_number TEXT,
        district TEXT,
        commodity TEXT,
        phone TEXT,
        verified INTEGER DEFAULT 0,
        rating REAL DEFAULT 0.0
    )
    """)
    
    # Create dealers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dealers (
        id TEXT PRIMARY KEY,
        shop_name TEXT,
        fertilizer INTEGER DEFAULT 0,
        seed INTEGER DEFAULT 0,
        pesticide INTEGER DEFAULT 0,
        location TEXT,
        verified INTEGER DEFAULT 0
    )
    """)
    # Create dealer_inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dealer_inventory (
        id TEXT PRIMARY KEY,
        dealer_id TEXT,
        item_name TEXT,
        category TEXT,
        price REAL,
        stock_quantity INTEGER,
        unit TEXT,
        FOREIGN KEY (dealer_id) REFERENCES dealers (id)
    )
    """)

    # Create reservations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id TEXT PRIMARY KEY,
        dealer_id TEXT,
        inventory_id TEXT,
        farmer_phone TEXT,
        quantity INTEGER,
        pin_code TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dealer_id) REFERENCES dealers (id),
        FOREIGN KEY (inventory_id) REFERENCES dealer_inventory (id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")
