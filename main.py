import sqlite3
from load_data import load_csv_to_sqlite
from schema_desc import build_schema_description
from agent_code import generate_sql_with_retries

MAX_ATTEMPTS = 3
QUESTION = "How many employees report to Neena Kochhar?"

def print_separator():
    print("=" * 100)


def print_attempt(attempt_record: dict, max_attempts: int):
    print(f"[Attempt {attempt_record['attempt']}/{max_attempts}]")
    print("SQL:")
    print("  " + attempt_record["sql"])
    print()
    if attempt_record["status"] == "SUCCESS":
        print("Result: SUCCESS")
        print("  " + str(attempt_record["result"]))
    else:
        print("Result: ERROR")
        print("  " + attempt_record["error"])
    print()

def format_result(rows):
    if not rows:
        return "(no rows)"
    if len(rows) == 1 and len(rows[0]) == 1:
        return str(rows[0][0])
    return str(rows)

def main():
    conn = sqlite3.connect(":memory:")
    load_csv_to_sqlite("employee_dataset.csv", conn)
    schema_description = build_schema_description(conn)

    print_separator()
    print(" Question: " + QUESTION)
    print_separator()
    print()

    result = generate_sql_with_retries(
        QUESTION, schema_description, conn, MAX_ATTEMPTS
    )

    for attempt_record in result["attempt_history"]:
        print_attempt(attempt_record, MAX_ATTEMPTS)

    print_separator()
    if result["success"]:
        corrected = result["attempts_used"] - 1
        print(" Final answer: " + str(result["rows"]))
        print(
            f" ({result['attempts_used']} attempts, {corrected} failures corrected)"
        )
    else:
        print(f" FAILED after {MAX_ATTEMPTS} attempts")
    print_separator()


if __name__ == "__main__":
    main()