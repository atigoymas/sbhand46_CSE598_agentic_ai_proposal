import os
from google import genai
from dotenv import load_dotenv
import sqlite3

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

client = genai.Client(api_key=API_KEY)

def strip_markdown_fence(text):
    stripped = text.strip()
    if stripped.startswith("```"):
        line = stripped.splitlines()
        line.pop(0)
        content = "\n".join(line).strip()
        if content.endswith("```"):
            content = content[:-3].strip()
        print("Warning: A fence was detected and stripped.")
        return (content, True)
    else:
        return (stripped, False)

def build_prompt(question, schema_desc, previous_sql, previous_error):
    base_instructions = (
    f"You are a SQLite SQL generator.\n"
        f"Schema:\n{schema_desc}\n\n"
        f"Question:\n{question}\n\n"
        f"Respond with ONLY raw SQL, no markdown fences, no explanation."
        )

    prompt = base_instructions
    if previous_sql is not None:
        prompt += (
            f"\n\nYour previous SQL was:\n{previous_sql}\n\n"
            f"It failed with this error:\n{previous_error}\n\n"
            f"Correct it."
        )

    return prompt

def  generate_sql_with_retries(question, schema_desc, conn, max_attempts=3):
    attempt_history = []
    previous_sql = None
    previous_error = None

    for attempt_number in range(1, max_attempts + 1):
        prompt = build_prompt(question, schema_desc, previous_sql, previous_error)

        response = client.models.generate_content(model= GEMINI_MODEL, contents=prompt)
        raw_text = response.text
        cleaned_text, was_fenced = strip_markdown_fence(raw_text)
        sql = cleaned_text

        try:
            cur = conn.execute(sql)
            rows = cur.fetchall()

            attempt_history.append({"attempt": attempt_number, "sql": sql, "status": "SUCCESS", "result": rows})

            return {"success": True, "rows": rows, "attempt_history": attempt_history, "attempts_used": attempt_number}

        except sqlite3.Error as e:
            error_msg = str(e)
            attempt_history.append({"attempt": attempt_number, "sql": sql, "status": "ERROR", "error": error_msg})

            previous_sql = sql
            previous_error = error_msg

    return { "success": False, "rows": None, "attempt_history": attempt_history, "attempts_used": max_attempts}

if __name__ == "__main__":
    import sqlite3
    from load_data import load_csv_to_sqlite
    from schema_desc import build_schema_description

    conn = sqlite3.connect(":memory:")
    load_csv_to_sqlite("employee_dataset.csv", conn)
    schema_description = build_schema_description(conn)

    result = generate_sql_with_retries("How many employees report to Neena Kochhar?", schema_description, conn)

    print (result["success"], result["attempts_used"])
    print (result["rows"] if result["success"] else result["attempt_history"])