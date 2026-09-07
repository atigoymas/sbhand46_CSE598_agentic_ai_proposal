# NL-SQL Self-Correcting Agent

A natural-language-to-SQL agent with execution-feedback self-correction: it generates SQL for a question, executes it against SQLite, and, if execution fails, feeds the error back to the model and retries, up to a bounded number of attempts.

## Setup

1. Clone the repository and `cd` into it.
2. Create a virtual environment:
   ```
   py -3 -m venv .venv
   ```
3. Activate it:
   ```
   .venv\Scripts\Activate.ps1
   ```
   (If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first.)
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the repository root with:
   ```
   GOOGLE_API_KEY=<your Gemini API key>
   GEMINI_MODEL=<a Gemini model you have access to, e.g. gemini-3.5-flash>
   ```
   Get an API key from [Google AI Studio](https://aistudio.google.com/).

## Run

```
python main.py
```

This runs a fixed test question ("How many employees report to Neena Kochhar?") through the full pipeline and prints a boxed, numbered log of every generation attempt.

## Files

| File | Purpose |
|---|---|
| `employee_dataset.csv` | **Input file**/Dataset: Oracle HR sample `employees` table (50 rows) |
| `load_data.py` | Loads the CSV into an in-memory SQLite table using an explicit, hardcoded schema |
| `schema_desc.py` | Builds the schema description text sent to the model (column list, `JOB_ID` pattern description, dynamic distinct-value lists) |
| `agent_code.py` | `generate_sql_with_retries(...)`, the self-correcting SQL generation loop |
| `main.py` | Entry point; wires everything together and prints the boxed attempt log|
**Output prints out at the terminal itself after executing main.py**.
```
python main.py
```

## Known setup limitations

- The dataset is loaded fresh into an in-memory SQLite database on every run; nothing is persisted between runs.
- `GEMINI_MODEL` has no hardcoded default; it must be set in `.env` or the run will fail with a missing-model error.
