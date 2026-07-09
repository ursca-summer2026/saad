"""Tests for detect_pronoun(), the function that measures gender bias.

This function is the heart of the research: every chart in the dashboard is
built from its output. If it is wrong, every conclusion is wrong. So we check
it against hand-written examples where we already know the right answer.

Run it from the `streamlit` folder with:
    ./venv/bin/python test_detect_pronoun.py

It prints one line per test and exits with an error if any test fails.
"""

# Importing bias_app also runs the dashboard code once, which is harmless here
# (Streamlit does nothing when it is not serving a page). We import the real
# function rather than a copy, so this test always checks the code the app uses.
from bias_app import detect_pronoun


# Each case is: (the response text, the group we expect back, why it matters)
CASES = [
    # --- the basics -------------------------------------------------------
    ("He is a doctor.",                    "he/him",    "simple male"),
    ("She is a nurse.",                    "she/her",   "simple female"),
    ("They work long hours.",              "they/them", "simple neutral"),
    ("A nurse cares for patients.",        "none",      "no pronoun at all"),

    # --- every word in each group is recognised ---------------------------
    ("I spoke to him.",                    "he/him",    "him"),
    ("That is his bag.",                   "he/him",    "his"),
    ("I spoke to her.",                    "she/her",   "her"),
    ("The bag is hers.",                   "she/her",   "hers"),
    ("I met them.",                        "they/them", "them"),
    ("That is their bag.",                 "they/them", "their"),

    # --- BUG 1: order must not decide the answer --------------------------
    # The old code checked he/him first and returned immediately, so both of
    # these were labelled "he/him" no matter which pronoun came first.
    ("He is a doctor and she is a nurse.", "both", "he before she -> both"),
    ("She is a doctor and he is a nurse.", "both", "she before he -> both"),

    # --- BUG 2: punctuation must not hide a pronoun -----------------------
    # The old code only stripped "." and "," so these all came back "none".
    ("Nurses help patients-they listen.",  "they/them", "dash stuck to word"),
    ("They listen; they care.",            "they/them", "semicolon"),
    ("He's a doctor.",                     "he/him",    "apostrophe/contraction"),
    ("(She) is a lawyer.",                 "she/her",   "parentheses"),
    ('"They" are engineers.',              "they/them", "quote marks"),

    # --- a pronoun must be a whole word, not part of one ------------------
    ("The theatre is there.",              "none",      "'the'/'there' are not 'he'"),
    ("This is a shed.",                    "none",      "'shed' is not 'she'"),
    ("Hierarchy matters.",                 "none",      "'hierarchy' is not 'hi'"),

    # --- a gendered pronoun outranks a neutral one ------------------------
    ("A doctor helps. He listens. They care.", "he/him",
     "gendered wins over they"),
    ("A nurse helps. She listens. They care.", "she/her",
     "gendered wins over they"),

    # --- case does not matter ---------------------------------------------
    ("HE IS A DOCTOR.",                    "he/him",    "uppercase"),
    ("ShE iS a NuRsE.",                    "she/her",   "mixed case"),

    # --- empty input does not crash ---------------------------------------
    ("",                                   "none",      "empty response"),
]


def main():
    failures = 0
    for text, expected, why in CASES:
        actual = detect_pronoun(text)
        if actual == expected:
            print(f"  PASS  {why}")
        else:
            failures += 1
            print(f"  FAIL  {why}")
            print(f"          text     : {text!r}")
            print(f"          expected : {expected}")
            print(f"          got      : {actual}")

    total = len(CASES)
    print()
    if failures:
        print(f"{failures} of {total} tests FAILED")
        raise SystemExit(1)
    print(f"All {total} tests passed.")


if __name__ == "__main__":
    main()
