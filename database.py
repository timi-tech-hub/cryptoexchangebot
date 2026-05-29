import sqlite3
import json
import os

# Use /data folder for Render Persistent Disk, fallback to current dir for local dev
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)
DB_PATH = os.path.join(DB_DIR, "exchange.db")

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        phone TEXT,
        bank_name TEXT,
        bank_account_name TEXT,
        bank_account_number TEXT,
        crypto_address TEXT,
        naira_balance INTEGER DEFAULT 0,
        usdt_balance REAL DEFAULT 0,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,  -- 'sell', 'buy', 'withdraw_naira', 'withdraw_crypto', 'deposit'
        amount_currency TEXT,  -- 'USDT', 'NGN'
        amount REAL,
        rate REAL,
        status TEXT,  -- 'pending', 'completed', 'failed'
        tx_hash TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Settings table (for rates)
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    # Migration: Add details column to transactions if it doesn't exist
    try:
        c.execute("ALTER TABLE transactions ADD COLUMN details TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    # Insert default rates if not exist
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('buy_rate', '1480')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('sell_rate', '1520')")
    conn.commit()
    conn.close()

def get_user(user_id):
    """Retrieve user details by ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        columns = ['user_id', 'phone', 'bank_name', 'bank_account_name', 'bank_account_number', 'crypto_address', 'naira_balance', 'usdt_balance', 'registered_at']
        return dict(zip(columns, user))
    return None

def register_user(user_id, phone, bank_name, bank_account_name, bank_account_number, crypto_address):
    """Register a new user or update existing"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users 
        (user_id, phone, bank_name, bank_account_name, bank_account_number, crypto_address)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, phone, bank_name, bank_account_name, bank_account_number, crypto_address))
    conn.commit()
    conn.close()

def auto_create_user(user_id):
    """Ensure user exists in DB, create with defaults if not"""
    user = get_user(user_id)
    if not user:
        register_user(user_id, "", "", "", "", "")
        user = get_user(user_id)
    return user

def update_balance(user_id, naira_delta=0, usdt_delta=0):
    """Update user's Naira and/or USDT balance"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET naira_balance = naira_balance + ?, usdt_balance = usdt_balance + ? WHERE user_id = ?",
              (naira_delta, usdt_delta, user_id))
    conn.commit()
    conn.close()

def add_transaction(user_id, tx_type, amount_currency, amount, rate, status, tx_hash=None, details=None):
    """Add a new transaction record"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO transactions (user_id, type, amount_currency, amount, rate, status, tx_hash, details)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, tx_type, amount_currency, amount, rate, status, tx_hash, details))
    conn.commit()
    tx_id = c.lastrowid
    conn.close()
    return tx_id

def update_transaction_status(tx_id, status):
    """Update transaction status (pending -> completed, etc.)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE transactions SET status = ? WHERE id = ?", (status, tx_id))
    conn.commit()
    conn.close()

def get_transaction(tx_id):
    """Retrieve transaction details"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    tx = c.fetchone()
    conn.close()
    if tx:
        columns = ['id', 'user_id', 'type', 'amount_currency', 'amount', 'rate', 'status', 'tx_hash', 'details', 'created_at']
        return dict(zip(columns, tx))
    return None

def get_user_transactions(user_id, limit=10):
    """Get user's transaction history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
    txs = c.fetchall()
    conn.close()
    columns = ['id', 'user_id', 'type', 'amount_currency', 'amount', 'rate', 'status', 'tx_hash', 'created_at']
    return [dict(zip(columns, tx)) for tx in txs]

def get_setting(key):
    """Retrieve a setting value"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_setting(key, value):
    """Set or update a setting"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_all_users():
    """Get all registered users (for broadcasting, etc.)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    return [user[0] for user in users]
