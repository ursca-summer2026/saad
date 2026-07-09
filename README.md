# AI Bias Research

Materials for the URSCA Summer 2026 project.

A research project studying **gender bias in AI language models** — how models implicitly assume the gender of people in different professions, measured through the pronouns they use. The workflow has three stages: collect model responses, load them into a SQLite database, and analyze them in an interactive dashboard.

Each response is sorted into one of four groups: **he/him**, **she/her**, **they/them**, or **none** (no pronoun at all). When a response mentions more than one gender, the one mentioned most often wins. A profession whose responses lean heavily to `he/him` or `she/her` is one the models are assuming a gender for.

## Repository Structure

| Folder | What it does |
|--------|--------------|
| `biasDatabase/` | Builds and queries the SQLite database from the CSV data |
| `streamlit/` | Interactive dashboard that visualizes the bias analysis |
| `ainslee/` | Response-collection tool that generates the per-model CSVs |

## The Data (CSV Format)

Each model's responses live in one CSV file named after the model (e.g. `phi.csv`). Every file has the same four columns:

| Column | Description |
|--------|-------------|
| `rowIndex` | Response number |
| `keyword` | The profession keyword in the prompt (e.g. Nurse, Doctor, Lawyer, Engineer) |
| `prompt` | The input prompt given to the model |
| `response` | The model's answer |

Current datasets: `phi.csv`, `llama32.csv`, `qwencodernext.csv`.

## Building the Database (`biasDatabase/`)

The database has three normalized tables:

- **models** — model names (taken from the CSV filenames)
- **keywords** — the profession keywords used in prompts
- **responses** — each prompt/response pair, linked to a model and keyword via foreign keys

Every `<model>.csv` in the `biasDatabase/` folder is auto-discovered and loaded, so adding a model needs no code changes. The generated `bias_research.db` is rebuilt from the CSVs (and is git-ignored).

### How to run

```
cd biasDatabase
python3 create_database.py
```

### Available Commands

| Command | Description |
|---------|-------------|
| `python3 create_database.py` | Create/rebuild the database from the CSV files and display stats |
| `python3 create_database.py --stats` | Display statistics on an existing database |
| `python3 create_database.py --model <name>` | Show all responses from a specific model (e.g. `--model phi`) |
| `python3 create_database.py --keyword <word>` | Show all responses for a specific keyword (e.g. `--keyword Nurse`) |
| `python3 create_database.py --help` | Show all available commands |

### Adding a New Model

1. Create a CSV named after the model (e.g. `gemini.csv`)
2. Use the format `rowIndex,keyword,prompt,response`
3. Drop it into the `biasDatabase/` folder — it is auto-discovered (no code changes needed)
4. Run `python3 create_database.py`

Step 4 is required. The dashboard reads the **database**, not the CSV files, so a new CSV does not appear until the database is rebuilt. After that the dashboard picks the model up on its own — model names, keyword lists, filters and chart colours are all read from the data.

Two current limits worth knowing: the dashboard has **8 model colours**, so a 9th model would run out; and a CSV placed in `biasDatabase/_excluded/` is deliberately ignored (subfolders are not searched).

## Analysis Dashboard (`streamlit/`)

An interactive Streamlit app that reads the database and visualizes the bias:

- Browse every response, filtered by model
- Pronoun usage compared between models (bar chart)
- Bias by profession (heatmap)
- Model-vs-model comparison (heatmap)
- Gender references per prompt, compared across models (percentages)

### How to run

```
cd streamlit
source venv/bin/activate
streamlit run bias_app.py
```

### Testing the bias metric

Every chart is built from one function, `detect_pronoun()`, so if it is wrong then every conclusion is wrong. `test_detect_pronoun.py` checks it against hand-written examples where the correct answer is already known — including responses that mention more than one gender, and pronouns hidden behind punctuation such as `he's` or `—they`.

```
cd streamlit
./venv/bin/python test_detect_pronoun.py
```
