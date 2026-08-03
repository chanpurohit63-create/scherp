import sqlite3, sys

conn = sqlite3.connect('backend/dev.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print("Tables:", tables)

for t in ['user', 'school']:
    if t in tables:
        cur.execute(f"SELECT * FROM {t} LIMIT 20")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        print(f"\n{t} columns:", cols)
        for r in rows:
            print(r)