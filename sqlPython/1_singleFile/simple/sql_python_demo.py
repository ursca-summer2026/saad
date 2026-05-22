import sqlite3

def create_schema():
    try:
        # Connect to 'example.db' (creates it if it doesn't exist)
        with sqlite3.connect('example.db') as conn:
            cursor = conn.cursor()
            
            # Define your schema using SQL CREATE TABLE statements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            print("Schema created successfully!")
            
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_schema()

