import sqlite3
import os

# Print current working directory
print("Current working directory:", os.getcwd())

# List files in the current directory
print("Files in current directory:", os.listdir('.'))

# Try to connect to the database
try:
    conn = sqlite3.connect('ragchat.db')
    c = conn.cursor()
    
    # List all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print("Tables in database:", tables)
    
    # Try to query if we have tables
    if tables:
        for table in tables:
            try:
                c.execute(f"SELECT * FROM {table[0]}")
                rows = c.fetchall()
                print(f"Data in {table[0]}:", rows)
            except Exception as e:
                print(f"Error querying {table[0]}:", e)
    
    conn.close()
except Exception as e:
    print("Error connecting to database:", e)