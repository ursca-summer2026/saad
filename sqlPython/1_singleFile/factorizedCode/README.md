# SQLite Python Demo - Random Data Generation

A Python demonstration project showing how to create a SQLite database, define a schema with relationships, and populate it with randomly generated data.

## Features

- ✨ **Clean Code Architecture**: Modular functions following Python best practices
- 📝 **Type Hints**: Full type annotations for better code clarity
- 🎲 **Random Data Generation**: Automatically generates realistic user and post data
- 🔗 **Foreign Key Relations**: Demonstrates table relationships
- 📊 **Statistics Display**: Shows database contents after population
- 🛡️ **Error Handling**: Robust exception handling for database operations
- 📚 **Comprehensive Documentation**: Detailed docstrings for all functions

## Database Schema

### Users Table
- `id`: Primary key (auto-increment)
- `name`: User's full name
- `email`: Unique email address
- `created_at`: Timestamp of creation

### Posts Table
- `id`: Primary key (auto-increment)
- `user_id`: Foreign key referencing users table
- `title`: Post title
- `content`: Post content
- `created_at`: Timestamp of creation

## Requirements

- Python 3.7+
- sqlite3 (included in Python standard library)

No external dependencies required!

## Usage

Run the script to create the database and populate it with random data:

```bash
python sql_insert_python_demo.py
```

### Expected Output

```
SQLite Database Demo - Random Data Generation
--------------------------------------------------
✓ Schema created successfully!

Generating random data...

Inserting data into database...
✓ Inserted 15 users
✓ Inserted 45 posts

==================================================
DATABASE STATISTICS
==================================================
Total Users: 15
Total Posts: 45

Sample Users:
  - Alice Smith (alice.smith123@example.com)
  - Bob Johnson (bob.johnson456@example.com)
  - Charlie Williams (charlie.williams789@example.com)

Sample Posts:
  - 'Getting Started with Python' by Alice Smith
  - 'Understanding SQLite Databases' by Bob Johnson
  - 'Best Practices for Code Organization' by Charlie Williams
==================================================

✓ Database setup completed successfully!
Database connection closed.
```

## Code Structure

### Main Functions

- **`create_connection()`**: Establishes database connection
- **`create_schema()`**: Creates database tables
- **`generate_random_users()`**: Generates random user data
- **`generate_random_posts()`**: Generates random post data
- **`insert_users()`**: Inserts user records into database
- **`insert_posts()`**: Inserts post records into database
- **`display_statistics()`**: Shows database statistics
- **`main()`**: Orchestrates the entire workflow

### Configuration

You can modify the following constants in the `main()` function:

```python
DB_NAME = 'example.db'          # Database file name
NUM_USERS = 15                  # Number of users to generate
POSTS_PER_USER = 3              # Average posts per user
```

## Python Best Practices Implemented

1. **Type Hints**: All functions include parameter and return type annotations
2. **Docstrings**: Comprehensive Google-style docstrings for all functions
3. **Error Handling**: Try-except blocks with specific error types
4. **PEP 8 Compliance**: Follows Python style guidelines
5. **Separation of Concerns**: Each function has a single, well-defined purpose
6. **Constants**: Configuration values defined clearly
7. **Context Management**: Proper resource cleanup
8. **Meaningful Names**: Clear, descriptive variable and function names

## Database Operations

### Querying the Database

After running the script, you can query the database using SQLite tools:

```bash
# Open database with SQLite CLI
sqlite3 example.db

# Example queries
SELECT * FROM users;
SELECT * FROM posts WHERE user_id = 1;
SELECT u.name, COUNT(p.id) as post_count 
FROM users u 
LEFT JOIN posts p ON u.id = p.user_id 
GROUP BY u.id;
```

### Resetting the Database

To start fresh, simply delete the database file:

```bash
rm example.db
```

Then run the script again.

## Customization (Challenges!)

### Adding More Data Fields

1. Update the schema in `create_schema()`
2. Modify the data generation functions
3. Update the insert functions with new fields

### Changing Data Generation

Modify the sample data arrays in:

- `generate_random_users()`: Edit `first_names` and `last_names` lists
- `generate_random_posts()`: Edit `post_titles` and `post_content_templates` lists

## Error Handling

The script handles common SQLite errors:

- **Duplicate emails**: Automatically skipped during insertion
- **Connection errors**: Caught and reported with clear messages
- **Schema errors**: Graceful failure with error details
