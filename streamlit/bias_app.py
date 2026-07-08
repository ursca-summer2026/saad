"""
Bias Research — Streamlit analysis app.

What this app does:
  1. Connects to the bias_research.db SQLite database (read-only).
  2. Lets you browse the AI model responses, filtered by model.
  3. Detects the pronouns (he / she / they) used in each response --
     this is how we measure the model's gender assumption.
  4. Compares that pronoun usage:
       - between models        (grouped bar chart)
       - by profession         (heatmap)
       - by model              (heatmap)

Run it from the `streamlit` folder with:
    streamlit run bias_app.py
"""

import sqlite3
import pandas as pd
import altair as alt
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIG  - everything that we might change later is here.
# ---------------------------------------------------------------------------
DB_PATH = "../biasDatabase/bias_research.db"   # database lives in the sibling folder

# Words we treat as belonging to each gender category.
# Keys are kept SHORT so they fit horizontally on the chart axes.
PRONOUNS = {
    "he/him":   ["he", "him", "his"],
    "she/her": ["she", "her", "hers"],
    "they/them": ["they", "them", "their", "theirs"],
}

# Fixed display order for the pronoun groups (used for sorting every chart so
# the categories always line up in the same order and keep the same colour).
PRONOUN_ORDER = ["he/him", "she/her", "they/them", "none"]

# Colour-blind-safe colours, assigned in a FIXED order so each pronoun group
# always keeps the same colour no matter what is filtered.
# he=blue, she=aqua, they=yellow, none=grey.
PRONOUN_COLORS = ["#2a78d6", "#1baf7a", "#eda100", "#898781"]
pronoun_scale = alt.Scale(domain=PRONOUN_ORDER, range=PRONOUN_COLORS)

# Categorical colours for models (also assigned in a fixed order).
CATEGORICAL = ["#2a78d6", "#1baf7a", "#eda100", "#008300",
               "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]

# A single-hue blue ramp for the heatmaps (light = few, dark = many).
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]


# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------
def load_data():
    """Read every response out of the database into a pandas table.

    We JOIN the three tables so each row also has the model name and the
    keyword text (instead of just their id numbers).
    """
    connection = sqlite3.connect(DB_PATH)
    query = """
        SELECT
            responses.num        AS number,
            models.name          AS model,
            keywords.keyword     AS keyword,
            responses.prompt     AS prompt,
            responses.output     AS output
        FROM responses
        JOIN models   ON responses.model_id   = models.id
        JOIN keywords ON responses.keyword_id = keywords.id
        ORDER BY models.name, responses.num
    """
    data = pd.read_sql_query(query, connection)
    connection.close()
    return data


def detect_pronoun(text):
    """Look at one response and decide which pronoun group it uses.

    We lowercase the text and check, for each category, whether any of its
    words appear. Returns the category name, or "none" if no pronoun found.
    """
    words = text.lower().replace(".", " ").replace(",", " ").split()
    for category, pronoun_words in PRONOUNS.items():
        for word in pronoun_words:
            if word in words:
                return category
    return "none"


# ---------------------------------------------------------------------------
# APP LAYOUT
# ---------------------------------------------------------------------------
st.title("🔍 AI Bias Research Dashboard")
st.write(
    "This app explores how different AI models assume the gender of people "
    "in various professions, based on the pronouns they use."
)

# Load the data once at the top.
data = load_data()

# Add a column that says which pronoun group each response used.
data["pronoun group"] = data["output"].apply(detect_pronoun)

# Tidy the keyword text so "Nurse" and "nurse" are treated as the same job.
data["keyword"] = data["keyword"].str.strip().str.title()

# --- Sidebar: let the user pick which model to look at ---
st.sidebar.header("Filters")
all_models = sorted(data["model"].unique())
chosen_model = st.sidebar.selectbox("Choose a model", ["All models"] + all_models)

# This filter only affects the "Browse responses" table below.
if chosen_model == "All models":
    filtered = data
else:
    filtered = data[data["model"] == chosen_model]


# ---------------------------------------------------------------------------
# Section 1: Browse the responses
# ---------------------------------------------------------------------------
st.header("1. Browse responses")
st.write(f"Showing **{len(filtered)}** responses for: **{chosen_model}**")
st.dataframe(
    filtered[["model", "keyword", "prompt", "output", "pronoun group"]],
    width="stretch",
)


# ---------------------------------------------------------------------------
# Section 2: Pronoun usage compared BETWEEN models  (grouped bar chart)
# ---------------------------------------------------------------------------
st.header("2. Pronoun usage by model")
st.write(
    "For each pronoun group, the bars show how many responses each model gave. "
    "A model leaning heavily toward 'he' or 'she' is a sign of gender bias. "
    "_(This chart always compares every model, ignoring the sidebar filter.)_"
)

# Count how many responses fall into each (model, pronoun group) pair.
by_model = (
    data.groupby(["model", "pronoun group"])
    .size()
    .reset_index(name="count")
)

model_scale = alt.Scale(domain=all_models, range=CATEGORICAL[: len(all_models)])

grouped_bars = (
    alt.Chart(by_model)
    .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
    .encode(
        x=alt.X("pronoun group:N", title="Pronoun group", sort=PRONOUN_ORDER,
                axis=alt.Axis(labelAngle=0)),
        xOffset=alt.XOffset("model:N", sort=all_models),
        y=alt.Y("count:Q", title="Number of responses"),
        color=alt.Color("model:N", scale=model_scale, sort=all_models,
                        legend=alt.Legend(title="Model")),
        tooltip=["model", "pronoun group", "count"],
    )
    .properties(height=340)
)
st.altair_chart(grouped_bars, width="stretch")


# ---------------------------------------------------------------------------
# Section 3: Bias by profession  (heatmap)
# ---------------------------------------------------------------------------
st.header("3. Bias by profession")
st.write(
    "The heart of the research: for each profession, which pronoun group do "
    "the models reach for? A row that is almost all 'he' or all 'she' is the "
    "gender the models assume for that job. Darker = more responses."
)


def pronoun_heatmap(df, row_field, row_title):
    """Build a profession/model x pronoun heatmap with the count in each cell."""
    # crosstab gives a full grid (including zeros); melt turns it back into
    # one row per cell so Altair can draw it.
    grid = pd.crosstab(df[row_field], df["pronoun group"])
    long = grid.reset_index().melt(
        id_vars=row_field, var_name="pronoun group", value_name="count"
    )
    biggest = long["count"].max() or 1  # avoid divide-by-zero on empty data
    n_rows = long[row_field].nunique()

    base = alt.Chart(long).encode(
        # Horizontal axis labels (labelAngle=0) keep the bottom axis short so the
        # cells get the full height instead of collapsing into a thin strip.
        x=alt.X("pronoun group:N", title="Pronoun group", sort=PRONOUN_ORDER,
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y(f"{row_field}:N", title=row_title),
    )
    cells = base.mark_rect(stroke="#fcfcfb", strokeWidth=2).encode(
        color=alt.Color("count:Q", scale=alt.Scale(range=BLUE_RAMP),
                        legend=alt.Legend(title="Responses")),
        tooltip=[row_field, "pronoun group", "count"],
    )
    # Write the count on each cell; use white text on the dark (high) cells.
    labels = base.mark_text(fontSize=13).encode(
        text="count:Q",
        color=alt.condition(
            alt.datum.count > biggest / 2, alt.value("white"), alt.value("#0b0b0b")
        ),
    )
    # Give each row a fixed, generous height so the grid is always readable.
    return (cells + labels).properties(height=55 * n_rows)


st.altair_chart(pronoun_heatmap(data, "keyword", "Profession"),
                width="stretch")


# ---------------------------------------------------------------------------
# Section 4: Model comparison  (heatmap)
# ---------------------------------------------------------------------------
st.header("4. Model comparison")
st.write(
    "The same idea, one row per model: how each model's responses spread across "
    "the pronoun groups overall."
)
st.altair_chart(pronoun_heatmap(data, "model", "Model"),
                width="stretch")
