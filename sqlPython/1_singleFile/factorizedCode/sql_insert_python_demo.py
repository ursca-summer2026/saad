"""
SQLite Database Demo with Random Data Generation

This module demonstrates creating a SQLite database with a schema and
populating it with randomly generated data. It includes users and posts tables
with a foreign key relationship.

Author: Generated with best practices
Date: 2026-05-21
"""

import sqlite3
import random
from typing import List, Tuple
from datetime import datetime, timedelta


def create_connection(db_name: str = 'example_populated.db') -> sqlite3.Connection:
    """
    Create a database connection to the SQLite database.
    
    Args:
        db_name: Name of the database file (default: 'example_populated.db')
        
    Returns:
        Connection object to the database
        
    Raises:
        sqlite3.Error: If connection fails
    """
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def create_schema(conn: sqlite3.Connection) -> None:
    """
    Create the database schema with users and posts tables.
    
    Args:
        conn: SQLite database connection
        
    Raises:
        sqlite3.Error: If schema creation fails
    """
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create posts table with foreign key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✓ Schema created successfully!")
        
    except sqlite3.Error as e:
        print(f"Error creating schema: {e}")
        raise


def generate_random_users(count: int = 10) -> List[Tuple[str, str]]:
    """
    Generate random user data.
    
    Args:
        count: Number of users to generate (default: 10)
        
    Returns:
        List of tuples containing (name, email)
    """
    first_names = [
        "Alice", "Bob", "Charlie", "Diana", "Edward", 
        "Fiona", "George", "Hannah", "Isaac", "Julia",
        "Kevin", "Laura", "Michael", "Nina", "Oscar"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Anderson", "Taylor", "Thomas", "Moore", "Jackson"
    ]
    
    users = []
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com"
        users.append((name, email))
    
    return users


def generate_random_posts(user_count: int, posts_per_user: int = 3) -> List[Tuple[int, str, str]]:
    """
    Generate random post data.
    
    Args:
        user_count: Number of users (for user_id reference)
        posts_per_user: Average number of posts per user (default: 3)
        
    Returns:
        List of tuples containing (user_id, title, content)
    """
    post_titles = [
        "Getting Started with Python",
        "Understanding SQLite Databases",
        "Best Practices for Code Organization",
        "Introduction to Data Structures",
        "Web Development Tips",
        "Machine Learning Basics",
        "Debugging Techniques",
        "Clean Code Principles",
        "API Design Patterns",
        "Database Optimization",
        "Functional Programming",
        "Object-Oriented Design",
        "Testing Strategies",
        "Version Control with Git",
        "Agile Development Methods"
    ]
    
    post_content_templates = [
        "This is an insightful post about {}. It covers various aspects and provides useful examples.",
        "In this article, we explore {}. The concepts are explained with practical demonstrations.",
        "A comprehensive guide to {}. Learn the fundamentals and advanced techniques.",
        "Discover the power of {}. This post includes tips and best practices.",
        "Everything you need to know about {}. A detailed walkthrough with examples."
    ]
    
    posts = []
    total_posts = user_count * posts_per_user
    
    for _ in range(total_posts):
        user_id = random.randint(1, user_count)
        title = random.choice(post_titles)
        content = random.choice(post_content_templates).format(title.lower())
        posts.append((user_id, title, content))
    
    return posts


def insert_users(conn: sqlite3.Connection, users: List[Tuple[str, str]]) -> int:
    """
    Insert user data into the database.
    
    Args:
        conn: SQLite database connection
        users: List of tuples containing user data (name, email)
        
    Returns:
        Number of users inserted
        
    Raises:
        sqlite3.Error: If insertion fails
    """
    cursor = conn.cursor()
    inserted_count = 0
    
    try:
        for name, email in users:
            try:
                cursor.execute(
                    'INSERT INTO users (name, email) VALUES (?, ?)',
                    (name, email)
                )
                inserted_count += 1
            except sqlite3.IntegrityError:
                # Skip duplicate emails
                print(f"Skipping duplicate email: {email}")
                continue
        
        conn.commit()
        print(f"✓ Inserted {inserted_count} users")
        return inserted_count
        
    except sqlite3.Error as e:
        print(f"Error inserting users: {e}")
        raise


def insert_posts(conn: sqlite3.Connection, posts: List[Tuple[int, str, str]]) -> int:
    """
    Insert post data into the database.
    
    Args:
        conn: SQLite database connection
        posts: List of tuples containing post data (user_id, title, content)
        
    Returns:
        Number of posts inserted
        
    Raises:
        sqlite3.Error: If insertion fails
    """
    cursor = conn.cursor()
    
    try:
        cursor.executemany(
            'INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)',
            posts
        )
        conn.commit()
        print(f"✓ Inserted {len(posts)} posts")
        return len(posts)
        
    except sqlite3.Error as e:
        print(f"Error inserting posts: {e}")
        raise


def display_statistics(conn: sqlite3.Connection) -> None:
    """
    Display database statistics.
    
    Args:
        conn: SQLite database connection
    """
    cursor = conn.cursor()
    
    # Count users
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    # Count posts
    cursor.execute('SELECT COUNT(*) FROM posts')
    post_count = cursor.fetchone()[0]
    
    # Get sample data
    cursor.execute('SELECT name, email FROM users LIMIT 3')
    sample_users = cursor.fetchall()
    
    cursor.execute('''
        SELECT u.name, p.title 
        FROM posts p 
        JOIN users u ON p.user_id = u.id 
        LIMIT 3
    ''')
    sample_posts = cursor.fetchall()
    
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)
    print(f"Total Users: {user_count}")
    print(f"Total Posts: {post_count}")
    
    print("\nSample Users:")
    for name, email in sample_users:
        print(f"  - {name} ({email})")
    
    print("\nSample Posts:")
    for user_name, post_title in sample_posts:
        print(f"  - '{post_title}' by {user_name}")
    
    print("=" * 50)


def main() -> None:
    """
    Main function to orchestrate database creation and data population.
    """
    print("SQLite Database Demo - Random Data Generation")
    print("-" * 50)
    
    # Configuration
    DB_NAME = 'example_populated.db'
    NUM_USERS = 15
    POSTS_PER_USER = 3
    
    try:
        # Create connection
        conn = create_connection(DB_NAME)
        
        # Create schema
        create_schema(conn)
        
        # Generate random data
        print("\nGenerating random data...")
        users = generate_random_users(NUM_USERS)
        posts = generate_random_posts(NUM_USERS, POSTS_PER_USER)
        
        # Insert data
        print("\nInserting data into database...")
        insert_users(conn, users)
        insert_posts(conn, posts)
        
        # Display statistics
        display_statistics(conn)
        
        print("\n✓ Database setup completed successfully!")
        
    except sqlite3.Error as e:
        print(f"\n✗ Database error: {e}")
    
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()

