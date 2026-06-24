import sqlite3
import os
import csv
import sys
import glob

databaseFile = 'bias_research.db'
model_files = ['phi.csv', 'gpt4.csv', 'claude.csv']


def display_stats():
    if not os.path.exists(databaseFile):
        print(f"Error: {databaseFile} does not exist. Run without --stats first to create it.")
        return

    with sqlite3.connect(databaseFile) as conn:
        print(f"\n{'='*50}")
        print(f"  DATABASE STATISTICS: {databaseFile}")
        print(f"{'='*50}")

        # Record counts for each table
        tables = ['models', 'keywords', 'responses']
        print("\n--- Record Counts ---")
        for table in tables:
            count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            print(f"  {table}: {count} records")

        # List all models
        print("\n--- Models ---")
        rows = conn.execute('SELECT name FROM models').fetchall()
        for row in rows:
            print(f"  - {row[0]}")

        # List all keywords
        print("\n--- Keywords ---")
        rows = conn.execute('SELECT keyword FROM keywords').fetchall()
        for row in rows:
            print(f"  - {row[0]}")

        # Responses per model
        print("\n--- Responses Per Model ---")
        rows = conn.execute('''
            SELECT models.name, COUNT(responses.id)
            FROM models
            LEFT JOIN responses ON models.id = responses.model_id
            GROUP BY models.id
        ''').fetchall()
        for name, count in rows:
            print(f"  {name}: {count} responses")

        # Responses per keyword per model
        print("\n--- Responses Per Keyword Per Model ---")
        rows = conn.execute('''
            SELECT keywords.keyword, models.name, COUNT(responses.id)
            FROM responses
            JOIN keywords ON keywords.id = responses.keyword_id
            JOIN models ON models.id = responses.model_id
            GROUP BY keywords.keyword, models.name
            ORDER BY keywords.keyword, models.name
        ''').fetchall()
        for keyword, model, count in rows:
            print(f"  {keyword} + {model}: {count}")

        print(f"\n{'='*50}")
        print("  Database is ready for bias analysis.")
        print(f"{'='*50}\n")


def create_and_populate():
    # Step 1: Remove old database if it exists
    if os.path.exists(databaseFile):
        os.remove(databaseFile)
        print(f"Removed old {databaseFile}.")

    # Step 2: Read the schema file
    with open('schema.sql', 'r') as f:
        schema_script = f.read()

    # Step 3: Create the database and tables from schema.sql
    with sqlite3.connect(databaseFile) as conn:
        conn.executescript(schema_script)

    print(f"Database schema created successfully: {databaseFile}.")

    # Step 4: Load CSV files and populate the database
    with sqlite3.connect(databaseFile) as conn:
        for csv_file in model_files:
            # Model name comes from the filename (e.g., phi.csv -> phi)
            model_name = os.path.splitext(csv_file)[0]

            # Insert model into models table
            conn.execute('INSERT OR IGNORE INTO models (name) VALUES (?)', (model_name,))
            model_id = conn.execute('SELECT id FROM models WHERE name = ?', (model_name,)).fetchone()[0]

            # Read the CSV file
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header row

                for row in reader:
                    num = int(row[0])
                    prompt = row[1]
                    output = row[2]
                    keyword = row[3]

                    # Insert keyword into keywords table
                    conn.execute('INSERT OR IGNORE INTO keywords (keyword) VALUES (?)', (keyword,))
                    keyword_id = conn.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,)).fetchone()[0]

                    # Insert response into responses table
                    conn.execute(
                        'INSERT INTO responses (num, prompt, output, model_id, keyword_id) VALUES (?, ?, ?, ?, ?)',
                        (num, prompt, output, model_id, keyword_id)
                    )

            print(f"Loaded {csv_file} -> model: {model_name}")

        conn.commit()

    # Step 5: Run queries
    with sqlite3.connect(databaseFile) as conn:
        print("\n--- All Models ---")
        rows = conn.execute('SELECT * FROM models').fetchall()
        for row in rows:
            print(row)

        print("\n--- All Keywords ---")
        rows = conn.execute('SELECT * FROM keywords').fetchall()
        for row in rows:
            print(row)

        print("\n--- All Responses (with model and keyword names) ---")
        rows = conn.execute('''
            SELECT responses.num, responses.prompt, responses.output, models.name, keywords.keyword
            FROM responses
            JOIN models ON models.id = responses.model_id
            JOIN keywords ON keywords.id = responses.keyword_id
            ORDER BY models.name, responses.num
        ''').fetchall()
        for row in rows:
            print(row)

    # Step 6: Display statistics
    display_stats()


if __name__ == "__main__":
    if '--stats' in sys.argv:
        display_stats()
    else:
        create_and_populate()
