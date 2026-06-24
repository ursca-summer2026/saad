"""
create_database.py

Builds and populates a SQLite database for AI bias research.
Reads model response data from CSV files, where each CSV file
is named after the AI model (e.g., phi.csv, gpt4.csv, claude.csv).

Usage:
    python3 create_database.py                  Create/rebuild the database and display stats
    python3 create_database.py --stats          Display stats on an existing database
    python3 create_database.py --model phi      Show all responses from a specific model
    python3 create_database.py --keyword nurse  Show all responses for a specific keyword
    python3 create_database.py --help           Show all available commands
"""

import sqlite3
import os
import csv
import sys

# Database filename and list of model CSV files to load
databaseFile = 'bias_research.db'
model_files = ['phi.csv', 'gpt4.csv', 'claude.csv']


def display_help():
    """Show all available command line options."""
    print("""
Usage: python3 create_database.py [option]

Options:
  (no option)         Create/rebuild the database from CSV files and display stats
  --stats             Display statistics on an existing database
  --model <name>      Show all responses from a specific model (e.g., --model phi)
  --keyword <word>    Show all responses for a specific keyword (e.g., --keyword nurse)
  --help              Show this help message
""")


def query_by_model(model_name):
    """Show all responses from a specific model."""
    if not os.path.exists(databaseFile):
        print(f"Error: {databaseFile} does not exist. Run without options first to create it.")
        return

    with sqlite3.connect(databaseFile) as conn:
        # Check if the model exists in the database
        model = conn.execute('SELECT id FROM models WHERE name = ?', (model_name,)).fetchone()
        if not model:
            print(f"Error: Model '{model_name}' not found in the database.")
            print("Available models:")
            rows = conn.execute('SELECT name FROM models').fetchall()
            for row in rows:
                print(f"  - {row[0]}")
            return

        print(f"\n--- Responses from model: {model_name} ---")
        rows = conn.execute('''
            SELECT responses.num, responses.prompt, responses.output, keywords.keyword
            FROM responses
            JOIN models ON models.id = responses.model_id
            JOIN keywords ON keywords.id = responses.keyword_id
            WHERE models.name = ?
            ORDER BY responses.num
        ''', (model_name,)).fetchall()
        for num, prompt, output, keyword in rows:
            print(f"\n  #{num} [{keyword}]")
            print(f"  Prompt: {prompt}")
            print(f"  Output: {output}")

        print(f"\n  Total: {len(rows)} responses")


def query_by_keyword(keyword_name):
    """Show all responses for a specific keyword across all models."""
    if not os.path.exists(databaseFile):
        print(f"Error: {databaseFile} does not exist. Run without options first to create it.")
        return

    with sqlite3.connect(databaseFile) as conn:
        # Check if the keyword exists in the database
        keyword = conn.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword_name,)).fetchone()
        if not keyword:
            print(f"Error: Keyword '{keyword_name}' not found in the database.")
            print("Available keywords:")
            rows = conn.execute('SELECT keyword FROM keywords').fetchall()
            for row in rows:
                print(f"  - {row[0]}")
            return

        print(f"\n--- Responses for keyword: {keyword_name} ---")
        rows = conn.execute('''
            SELECT models.name, responses.prompt, responses.output
            FROM responses
            JOIN models ON models.id = responses.model_id
            JOIN keywords ON keywords.id = responses.keyword_id
            WHERE keywords.keyword = ?
            ORDER BY models.name
        ''', (keyword_name,)).fetchall()
        for model, prompt, output in rows:
            print(f"\n  [{model}]")
            print(f"  Prompt: {prompt}")
            print(f"  Output: {output}")

        print(f"\n  Total: {len(rows)} responses across {len(set(r[0] for r in rows))} models")


def display_stats():
    """Load an existing database and display statistics about its contents.
    Shows record counts, available models/keywords, and response breakdowns."""

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

        # List all models in the database
        print("\n--- Models ---")
        rows = conn.execute('SELECT name FROM models').fetchall()
        for row in rows:
            print(f"  - {row[0]}")

        # List all keywords used in prompts
        print("\n--- Keywords ---")
        rows = conn.execute('SELECT keyword FROM keywords').fetchall()
        for row in rows:
            print(f"  - {row[0]}")

        # How many responses each model has
        print("\n--- Responses Per Model ---")
        rows = conn.execute('''
            SELECT models.name, COUNT(responses.id)
            FROM models
            LEFT JOIN responses ON models.id = responses.model_id
            GROUP BY models.id
        ''').fetchall()
        for name, count in rows:
            print(f"  {name}: {count} responses")

        # Breakdown of responses by keyword and model
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
    """Create the database from scratch, load data from CSV files, run queries, and display stats."""

    # Step 1: Remove old database if it exists so we start fresh
    if os.path.exists(databaseFile):
        os.remove(databaseFile)
        print(f"Removed old {databaseFile}.")

    # Step 2: Read the schema file that defines our table structure
    with open('schema.sql', 'r') as f:
        schema_script = f.read()

    # Step 3: Create the database and tables from schema.sql
    with sqlite3.connect(databaseFile) as conn:
        conn.executescript(schema_script)

    print(f"Database schema created successfully: {databaseFile}.")

    # Step 4: Load each model's CSV file and insert data into the database
    with sqlite3.connect(databaseFile) as conn:
        for csv_file in model_files:
            # Model name comes from the filename (e.g., phi.csv -> phi)
            model_name = os.path.splitext(csv_file)[0]

            # Insert model into models table (IGNORE if it already exists)
            conn.execute('INSERT OR IGNORE INTO models (name) VALUES (?)', (model_name,))
            model_id = conn.execute('SELECT id FROM models WHERE name = ?', (model_name,)).fetchone()[0]

            # Read each row from the CSV and insert into the database
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip the header row (n, prompt, output, keyword)

                for row in reader:
                    num = int(row[0])
                    prompt = row[1]
                    output = row[2]
                    keyword = row[3]

                    # Insert keyword into keywords table (IGNORE if it already exists)
                    conn.execute('INSERT OR IGNORE INTO keywords (keyword) VALUES (?)', (keyword,))
                    keyword_id = conn.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,)).fetchone()[0]

                    # Insert the response, linking it to the model and keyword
                    conn.execute(
                        'INSERT INTO responses (num, prompt, output, model_id, keyword_id) VALUES (?, ?, ?, ?, ?)',
                        (num, prompt, output, model_id, keyword_id)
                    )

            print(f"Loaded {csv_file} -> model: {model_name}")

        conn.commit()

    # Step 5: Run queries to display all loaded data
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

    # Step 6: Display statistics before closing
    display_stats()


if __name__ == "__main__":
    if '--help' in sys.argv:
        display_help()
    elif '--stats' in sys.argv:
        display_stats()
    elif '--model' in sys.argv:
        idx = sys.argv.index('--model')
        if idx + 1 < len(sys.argv):
            query_by_model(sys.argv[idx + 1])
        else:
            print("Error: Please provide a model name. Example: --model phi")
    elif '--keyword' in sys.argv:
        idx = sys.argv.index('--keyword')
        if idx + 1 < len(sys.argv):
            query_by_keyword(sys.argv[idx + 1])
        else:
            print("Error: Please provide a keyword. Example: --keyword nurse")
    else:
        create_and_populate()
