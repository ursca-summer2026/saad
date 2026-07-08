Materials for the URSCA Summer 2026 project.


  # AI Bias Research

  Materials for the URSCA Summer 2026 project.

  A research project studying **gender bias in AI language models** — how models implicitly assume the gender of people in different
  professions, measured through the pronouns (he / she / they) they use. The workflow has three stages: collect model responses, load them into
  a SQLite database, and analyze them in an interactive dashboard.

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

  Every `<model>.csv` in the `biasDatabase/` folder is auto-discovered and loaded, so adding a model needs no code changes. The generated
  `bias_research.db` is rebuilt from the CSVs (and is git-ignored).

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

  ## Analysis Dashboard (`streamlit/`)

  An interactive Streamlit app that reads the database and visualizes the bias:

  - Browse every response, filtered by model
  - Pronoun usage compared between models (bar chart)
  - Bias by profession (heatmap)
  - Model-vs-model comparison (heatmap)

  ### How to run

  ```
  cd streamlit
  source venv/bin/activate
  streamlit run bias_app.py
  ```
