-- Database structure for the AI bias research project.
-- Three tables: one row per AI model, one per keyword (profession), and one
-- per response. Responses link back to a model and a keyword by their id, so
-- we never repeat the model/keyword text and can't mistype it.

-- The AI models we tested (e.g. phi, llama32, qwencodernext).
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,               -- model name, no duplicates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The professions we prompted about (Nurse, Doctor, Lawyer, Engineer).
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,            -- profession word, no duplicates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- One row for every response a model gave. This is the main table the
-- dashboard analyses for gender references.
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num INTEGER NOT NULL,                    -- the response's row number in its CSV
    prompt TEXT NOT NULL,                    -- the exact prompt that was asked
    output TEXT NOT NULL,                    -- what the model answered
    model_id INTEGER NOT NULL,               -- which model (-> models.id)
    keyword_id INTEGER NOT NULL,             -- which profession (-> keywords.id)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(id)
);
