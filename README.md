Materials for the URSCA Summer 2026 project.

# AI Bias Research Database

A SQLite database application for studying gender bias in AI model responses. The tool loads prompt/response data from CSV files, builds a relational database, and provides statistics and queries to determine if the data is ready for analysis.

## Project Structure

- `create_database.py` - Main script that creates, populates, and queries the database
- `schema.sql` - SQL file defining the database table structure (models, keywords, responses)
- `phi.csv`, `gpt4.csv`, `claude.csv` - CSV data files, each named after the AI model
- `bias_research.db` - The generated SQLite database (created by running the script)

## CSV File Format

Each CSV file is named after the AI model and contains the following columns:

| Column | Description |
|--------|-------------|
| n | Response number |
| prompt | The input prompt given to the model |
| output | The model's response |
| keyword | The keyword used in the prompt (e.g., nurse, doctor, engineer) |

## How to Run

First, navigate to the project directory:
cd ~/Schema


### Available Commands

| Command | Description |
|---------|-------------|
| `python3 create_database.py` | Create/rebuild the database from CSV files and display stats |
| `python3 create_database.py --stats` | Display statistics on an existing database |
| `python3 create_database.py --model <name>` | Show all responses from a specific model (e.g., `--model phi`) |
| `python3 create_database.py --keyword <word>` | Show all responses for a specific keyword (e.g., `--keyword nurse`) |
| `python3 create_database.py --help` | Show all available commands |

## Database Schema

The database has three tables:

- **models** - Stores AI model names (extracted from CSV filenames)
- **keywords** - Stores unique keywords used in prompts (e.g., nurse, doctor, engineer)
- **responses** - Stores each prompt/response pair, linked to a model and keyword via foreign keys

## Adding New Models

1. Create a new CSV file named after the model (e.g., `gemini.csv`)
2. Follow the CSV format: `n,prompt,output,keyword`
3. Add the filename to the `model_files` list in `create_database.py`
4. Run `python3 create_database.py`

saad...