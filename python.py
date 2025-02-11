import sqlite3

# Define SQLite database path
SQLITE_DB_PATH = "data_source.db"

# Connect to SQLite
conn = sqlite3.connect(SQLITE_DB_PATH)
cursor = conn.cursor()

# Create a table
cursor.execute("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert sample data
cursor.executemany("""
    INSERT INTO customers (name, email, age) VALUES (?, ?, ?)
""", [
    ("Alice Johnson", "alice@example.com", 28),
    ("Bob Smith", "bob@example.com", 34),
    ("Charlie Brown", "charlie@example.com", 45)
])

# Commit and close connection
conn.commit()
conn.close()

print(f"SQLite database created at: {SQLITE_DB_PATH}")
