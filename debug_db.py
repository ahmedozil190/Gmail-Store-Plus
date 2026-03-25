import sqlite3
import os

DB_PATH = "d:\\9- My Projects\\5- Selling Accounts Bot\\store_database.db"
con = sqlite3.connect(DB_PATH)
con.row_factory = sqlite3.Row
cur = con.cursor()

try:
    # Check table info
    info = cur.execute("PRAGMA table_info(users)").fetchall()
    print("SCHEMA:")
    for col in info:
        print(f"- {col['name']} ({col['type']})")

    # Check all rows
    rows = cur.execute("SELECT * FROM users").fetchall()
    print(f"\nTOTAL USERS: {len(rows)}")
    for r in rows:
        print(dict(r))
except Exception as e:
    print(f"ERROR: {e}")
finally:
    con.close()
