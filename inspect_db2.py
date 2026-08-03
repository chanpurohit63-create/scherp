import sqlite3
import os

db_path = "backend/dev.db"
print(f"Database: {db_path}, exists: {os.path.exists(db_path)}, size: {os.path.getsize(db_path)}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# List all tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
print(f"\nTables ({len(tables)}): {tables}")

# Check for user-related tables
for tname in tables:
    if 'user' in tname.lower():
        c.execute(f"SELECT * FROM {tname}")
        cols = [d[0] for d in c.description]
        rows = c.fetchall()
        print(f"\n{tname} ({len(rows)} rows):")
        print(f"  Columns: {cols}")
        for r in rows:
            print(f"  {r}")

conn.close()