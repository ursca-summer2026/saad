import sqlite3
import random
import os
import csv
import sys

databaseFile = 'school.db'


def display_stats():
    """Load the database and display statistics about what is stored."""
    if not os.path.exists(databaseFile):
        print(f"Error: {databaseFile} does not exist. Run without --stats first to create it.")
        return

    with sqlite3.connect(databaseFile) as conn:
        print(f"\n{'='*50}")
        print(f"  DATABASE STATISTICS: {databaseFile}")
        print(f"{'='*50}")

        # Record counts for each table
        tables = ['students', 'courses', 'enrollments']
        print("\n--- Record Counts ---")
        for table in tables:
            count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            print(f"  {table}: {count} records")

        # List all courses
        print("\n--- Courses Available ---")
        rows = conn.execute('SELECT title FROM courses').fetchall()
        for row in rows:
            print(f"  - {row[0]}")

        # Students per course
        print("\n--- Students Per Course ---")
        rows = conn.execute('''
            SELECT courses.title, COUNT(enrollments.student_id)
            FROM courses
            LEFT JOIN enrollments ON courses.id = enrollments.course_id
            GROUP BY courses.id
        ''').fetchall()
        for title, count in rows:
            print(f"  {title}: {count} students")

        # Grade distribution
        print("\n--- Grade Distribution ---")
        rows = conn.execute('''
            SELECT grade, COUNT(*) FROM enrollments GROUP BY grade ORDER BY grade
        ''').fetchall()
        for grade, count in rows:
            print(f"  {grade}: {count}")

        print(f"\n{'='*50}")
        print("  Database is ready for analysis.")
        print(f"{'='*50}\n")


def create_and_populate():
    """Create the database, populate it from CSV files, and run queries."""
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

    # Step 4: Load sample data from CSV files
    with open('students.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        sample_students = [(row[0], row[1]) for row in reader]

    with open('courses.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        sample_courses = [(row[0], row[1]) for row in reader]

    with open('grades.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        grades = [row[0] for row in reader]

    # Step 5: Insert data into the database
    with sqlite3.connect(databaseFile) as conn:
        for name, email in sample_students:
            conn.execute('INSERT INTO students (name, email) VALUES (?, ?)', (name, email))

        for title, description in sample_courses:
            conn.execute('INSERT INTO courses (title, description) VALUES (?, ?)', (title, description))

        for student_id in range(1, len(sample_students) + 1):
            course_id = random.randint(1, len(sample_courses))
            grade = random.choice(grades)
            conn.execute(
                'INSERT INTO enrollments (student_id, course_id, grade) VALUES (?, ?, ?)',
                (student_id, course_id, grade)
            )

        conn.commit()

    print(f"Added {len(sample_students)} students from students.csv.")
    print(f"Added {len(sample_courses)} courses from courses.csv.")
    print(f"Added random enrollments for each student.")

    # Step 6: Run queries
    print("\n--- All Students ---")
    with sqlite3.connect(databaseFile) as conn:
        rows = conn.execute('SELECT * FROM students;').fetchall()
        for row in rows:
            print(row)

    print("\n--- All Courses ---")
    with sqlite3.connect(databaseFile) as conn:
        rows = conn.execute('SELECT * FROM courses;').fetchall()
        for row in rows:
            print(row)

    print("\n--- Enrollments with Student Names and Course Titles ---")
    with sqlite3.connect(databaseFile) as conn:
        rows = conn.execute('''
            SELECT students.name, courses.title, enrollments.grade
            FROM enrollments
            JOIN students ON students.id = enrollments.student_id
            JOIN courses ON courses.id = enrollments.course_id;
        ''').fetchall()
        for row in rows:
            print(row)

    # Step 7: Display statistics
    display_stats()


if __name__ == "__main__":
    if '--stats' in sys.argv:
        display_stats()
    else:
        create_and_populate()
