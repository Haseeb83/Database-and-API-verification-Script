import sqlite3

# Create a fresh SQLite DB
conn = sqlite3.connect("dummy.db")
c = conn.cursor()

# Create users table
c.execute("DROP TABLE IF EXISTS users")
c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
)
""")

# Insert sample data
c.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com"))
c.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Bob", "bob@example.com"))

conn.commit()
conn.close()

print("✅ dummy.db initialized successfully.")
