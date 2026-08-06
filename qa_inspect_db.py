"""Inspect database state for QA testing"""
import sqlite3

conn = sqlite3.connect('backend/dev.db')
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print(f"Tables ({len(tables)}):")
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"  {t}: {count}")
    except Exception as e:
        print(f"  {t}: ERROR {e}")

# Check users
print("\nUsers:")
cur.execute("SELECT id, email, full_name, role, school_id, is_active FROM user ORDER BY id")
for r in cur.fetchall():
    print(f"  {r}")

# Check schools
print("\nSchools:")
cur.execute("SELECT id, school_name, school_code, status FROM school ORDER BY id")
for r in cur.fetchall():
    print(f"  {r}")

conn.close()