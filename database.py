import sqlite3
from datetime import datetime
import os
import secrets

# Use absolute path and allow override via environment variable for persistence (e.g., on Railway)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "store_database.db"))

def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    con = _conn()
    cur = con.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY,
            username        TEXT,
            full_name       TEXT,
            balance         REAL    DEFAULT 0,
            hold            REAL    DEFAULT 0,
            tasks_count     INTEGER DEFAULT 0,
            total_withdrawn REAL    DEFAULT 0,
            join_date       TEXT,
            language        TEXT    DEFAULT 'ar',
            currency        TEXT    DEFAULT 'USD',
            status          TEXT    DEFAULT 'active'
        )
    """)

    # Simple Migrations for existing database
    columns = [c['name'] for c in cur.execute("PRAGMA table_info(users)").fetchall()]
    if 'hold' not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN hold REAL DEFAULT 0")
    if 'tasks_count' not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN tasks_count INTEGER DEFAULT 0")
    if 'total_withdrawn' not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN total_withdrawn REAL DEFAULT 0")

    # Accounts Pool (The items for sale)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts_pool (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            public_id       INTEGER UNIQUE,
            email           TEXT    UNIQUE,
            password        TEXT,
            recovery_email  TEXT,
            status          TEXT    DEFAULT 'available', -- 'available', 'sold'
            price           REAL,
            added_at        TEXT,
            sold_at         TEXT,
            sold_to_user_id INTEGER
        )
    """)

    # Migration for public_id
    columns_acc = [c['name'] for c in cur.execute("PRAGMA table_info(accounts_pool)").fetchall()]
    if 'public_id' not in columns_acc:
        cur.execute("ALTER TABLE accounts_pool ADD COLUMN public_id INTEGER")
    
    # Fill empty public_ids with random 8-digit numbers
    empty_accs = cur.execute("SELECT id FROM accounts_pool WHERE public_id IS NULL").fetchall()
    for acc in empty_accs:
        new_pid = secrets.randbelow(90000000) + 10000000 # 10,000,000 to 99,999,999
        cur.execute("UPDATE accounts_pool SET public_id = ? WHERE id = ?", (new_pid, acc['id']))

    # Deposits (Top-ups)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deposits (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER,
            amount          REAL,
            method          TEXT,
            proof_link      TEXT, -- Transaction ID or image path/note
            status          TEXT    DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
            created_at      TEXT,
            reject_reason   TEXT,
            external_id     TEXT,   -- For Cryptomus UUID
            sender_phone    TEXT    -- Phone number used for Vodafone Cash transfer
        )
    """)

    # Migration: Add external_id column if it doesn't exist
    try:
        cur.execute("ALTER TABLE deposits ADD COLUMN external_id TEXT")
    except sqlite3.OperationalError:
        pass

    # Migration: Add sender_phone column if it doesn't exist
    try:
        cur.execute("ALTER TABLE deposits ADD COLUMN sender_phone TEXT DEFAULT ''")
        con.commit()
    except sqlite3.OperationalError:
        pass
    
    # Migration: Add egp_amount and exchange_rate columns if they don't exist
    try:
        cur.execute("ALTER TABLE deposits ADD COLUMN egp_amount REAL DEFAULT 0.0")
        cur.execute("ALTER TABLE deposits ADD COLUMN exchange_rate REAL DEFAULT 0.0")
        con.commit()
    except sqlite3.OperationalError:
        pass

    # Orders (History of purchases)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER,
            account_id      INTEGER,
            price_paid      REAL,
            purchased_at    TEXT,
            FOREIGN KEY(account_id) REFERENCES accounts_pool(id)
        )
    """)

    # Settings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    con.commit()
    con.close()

# ── User Helpers ─────────────────────────────────────────────────────────────
def get_user(user_id: int):
    con = _conn()
    row = con.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    con.close()
    return row

def create_user(user_id: int, username: str, full_name: str, language: str = 'ar'):
    con = _conn()
    con.execute(
        """INSERT OR IGNORE INTO users
           (user_id, username, full_name, balance, join_date, language)
           VALUES (?, ?, ?, 0, ?, ?)""",
        (user_id, username, full_name, datetime.now().isoformat(), language),
    )
    con.commit()
    con.close()

def update_user_language(user_id: int, language: str):
    con = _conn()
    con.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
    con.commit()
    con.close()

def adjust_user_balance(user_id: int, delta: float):
    con = _conn()
    con.execute("UPDATE users SET balance = ROUND(balance + ?, 2) WHERE user_id = ?", (delta, user_id))
    con.commit()
    con.close()

# ── Account Pool Helpers ──────────────────────────────────────────────────────
def add_account_to_pool(email, password, recovery_email="", price=0.50):
    con = _conn()
    try:
        # Generate unique 8-digit public_id
        while True:
            public_id = secrets.randbelow(90000000) + 10000000
            if not con.execute("SELECT 1 FROM accounts_pool WHERE public_id = ?", (public_id,)).fetchone():
                break
                
        con.execute(
            """INSERT INTO accounts_pool (public_id, email, password, recovery_email, price, added_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (public_id, email, password, recovery_email, price, datetime.now().isoformat())
        )
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        con.close()

def get_available_accounts_count():
    con = _conn()
    count = con.execute("SELECT COUNT(*) FROM accounts_pool WHERE status = 'available'").fetchone()[0]
    con.close()
    return count

def get_next_available_account(price_limit=None):
    con = _conn()
    if price_limit:
        row = con.execute(
            "SELECT * FROM accounts_pool WHERE status = 'available' AND price <= ? ORDER BY id LIMIT 1",
            (price_limit,)
        ).fetchone()
    else:
        row = con.execute("SELECT * FROM accounts_pool WHERE status = 'available' ORDER BY id LIMIT 1").fetchone()
    con.close()
    return row

# ── Purchase Helpers ──────────────────────────────────────────────────────────
def purchase_account(user_id: int, account_id: int):
    con = _conn()
    cur = con.cursor()
    try:
        # Get account details
        acc = cur.execute("SELECT * FROM accounts_pool WHERE id = ?", (account_id,)).fetchone()
        if not acc or acc['status'] != 'available':
            return False, "Account no longer available."

        # Get user balance
        user = cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not user or user['balance'] < acc['price']:
            return False, "Insufficient balance."

        # Perform transaction
        cur.execute("UPDATE users SET balance = ROUND(balance - ?, 2) WHERE user_id = ?", (acc['price'], user_id))
        cur.execute(
            "UPDATE accounts_pool SET status = 'sold', sold_at = ?, sold_to_user_id = ? WHERE id = ?",
            (datetime.now().isoformat(), user_id, account_id)
        )
        cur.execute(
            "INSERT INTO orders (user_id, account_id, price_paid, purchased_at) VALUES (?, ?, ?, ?)",
            (user_id, account_id, acc['price'], datetime.now().isoformat())
        )
        
        con.commit()
        return True, acc
    except Exception as e:
        con.rollback()
        return False, str(e)
    finally:
        con.close()

# ── Deposit Helpers ───────────────────────────────────────────────────────────
def create_deposit_request(user_id: int, amount: float, method: str, proof: str, sender_phone: str = '', egp_amount: float = 0.0, exchange_rate: float = 0.0):
    con = _conn()
    cur = con.cursor()
    cur.execute(
        """INSERT INTO deposits (user_id, amount, method, proof_link, created_at, sender_phone, egp_amount, exchange_rate)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, amount, method, proof, datetime.now().isoformat(), sender_phone, egp_amount, exchange_rate)
    )
    con.commit()
    dep_id = cur.lastrowid
    con.close()
    return dep_id

def approve_deposit(dep_id: int):
    con = _conn()
    cur = con.cursor()
    dep = cur.execute("SELECT * FROM deposits WHERE id = ?", (dep_id,)).fetchone()
    if not dep or dep['status'] != 'pending':
        con.close()
        return None

    cur.execute("UPDATE deposits SET status = 'approved' WHERE id = ?", (dep_id,))
    cur.execute("UPDATE users SET balance = ROUND(balance + ?, 2) WHERE user_id = ?", (dep['amount'], dep['user_id']))
    con.commit()
    con.close()
    return dict(dep)

def reject_deposit(dep_id: int, reason: str):
    con = _conn()
    cur = con.cursor()
    cur.execute("UPDATE deposits SET status = 'rejected', reject_reason = ? WHERE id = ?", (reason, dep_id))
    dep = cur.execute("SELECT * FROM deposits WHERE id = ?", (dep_id,)).fetchone()
    con.commit()
    con.close()
    return dict(dep) if dep else None

def get_deposit_by_external_id(ext_id: str):
    con = _conn()
    row = con.execute("SELECT * FROM deposits WHERE external_id = ?", (ext_id,)).fetchone()
    con.close()
    return row

def update_deposit_external_id(dep_id: int, ext_id: str):
    con = _conn()
    con.execute("UPDATE deposits SET external_id = ? WHERE id = ?", (ext_id, dep_id))
    con.commit()
    con.close()

def get_user_orders(user_id: int):
    con = _conn()
    rows = con.execute("""
        SELECT o.*, a.email, a.password, a.recovery_email 
        FROM orders o
        JOIN accounts_pool a ON o.account_id = a.id
        WHERE o.user_id = ?
        ORDER BY o.purchased_at DESC
    """, (user_id,)).fetchall()
    con.close()
    return rows

def purchase_bulk_accounts(user_id: int, quantity: int):
    import sqlite3
    con = _conn()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    try:
        # Check balance
        user = cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not user: return False, "User not found"
        
        # Get accounts
        accs = cur.execute(
            "SELECT * FROM accounts_pool WHERE status = 'available' LIMIT ?", 
            (quantity,)
        ).fetchall()
        
        if len(accs) < quantity:
            return False, f"Not enough accounts available ({len(accs)} left)"
            
        total_price = sum(a['price'] for a in accs)
        if user['balance'] < total_price:
            return False, "Insufficient balance"
            
        # Perform transaction
        cur.execute("UPDATE users SET balance = ROUND(balance - ?, 2) WHERE user_id = ?", (total_price, user_id))
        
        sold_accs = [dict(a) for a in accs]
        now = datetime.now().isoformat()
        for acc in sold_accs:
            cur.execute(
                "UPDATE accounts_pool SET status = 'sold', sold_at = ?, sold_to_user_id = ? WHERE id = ?",
                (now, user_id, acc['id'])
            )
            cur.execute(
                "INSERT INTO orders (user_id, account_id, price_paid, purchased_at) VALUES (?, ?, ?, ?)",
                (user_id, acc['id'], acc['price'], now)
            )
            
        con.commit()
        return True, sold_accs
    except Exception as e:
        con.rollback()
        return False, str(e)
    finally:
        con.close()
def get_admin_stats():
    con = _conn()
    try:
        total_users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_accounts = con.execute("SELECT COUNT(*) FROM accounts_pool").fetchone()[0]
        available_accounts = con.execute("SELECT COUNT(*) FROM accounts_pool WHERE status = 'available'").fetchone()[0]
        sold_accounts = con.execute("SELECT COUNT(*) FROM accounts_pool WHERE status = 'sold'").fetchone()[0]
        total_orders = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        pending_deposits = con.execute("SELECT COUNT(*) FROM deposits WHERE status = 'pending'").fetchone()[0]
        total_balance = con.execute("SELECT SUM(balance) FROM users").fetchone()[0] or 0
        
        return {
            "total_users": total_users,
            "total_accounts": total_accounts,
            "available_accounts": available_accounts,
            "sold_accounts": sold_accounts,
            "total_orders": total_orders,
            "pending_deposits": pending_deposits,
            "total_balance": round(total_balance, 2)
        }
    finally:
        con.close()

def get_all_users():
    con = _conn()
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute("SELECT * FROM users ORDER BY join_date DESC").fetchall()]
    finally:
        con.close()

def get_all_accounts():
    con = _conn()
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute("SELECT * FROM accounts_pool ORDER BY id DESC").fetchall()]
    finally:
        con.close()

def get_all_deposits():
    con = _conn()
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute("SELECT * FROM deposits ORDER BY status='pending' DESC, created_at DESC").fetchall()]
    finally:
        con.close()

def get_user_wallet_history(user_id: int):
    con = _conn()
    con.row_factory = sqlite3.Row
    try:
        # Get Deposits
        deposits = [dict(r) for r in con.execute("SELECT * FROM deposits WHERE user_id = ?", (user_id,)).fetchall()]
        for d in deposits: d['type'] = 'deposit'
        
        # Get Orders
        orders = [dict(r) for r in con.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,)).fetchall()]
        for o in orders: o['type'] = 'purchase'
        
        # Combine and Sort
        history = deposits + orders
        history.sort(key=lambda x: x['created_at'], reverse=True)
        return history
    finally:
        con.close()

def get_user_deposits(user_id: int):
