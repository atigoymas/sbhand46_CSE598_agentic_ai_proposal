from load_data import SCHEMA, TABLE_NAME

JOB_ID_PATTERN_DESCRIPTION = (
    "JOB_ID values are codes formed by joining an abbreviation of a "
    "department/functional area with an abbreviation of a job role, "
    "separated by an underscore (pattern: <AREA>_<ROLE>)."
)

def build_schema_description(conn):
    lines = []

    for name, sql_type, _ in SCHEMA:
        lines.append(f"{name}:{sql_type}")
        
    lines.append(JOB_ID_PATTERN_DESCRIPTION)

    cur = conn.execute(f"SELECT DISTINCT JOB_ID FROM {TABLE_NAME} ORDER BY JOB_ID")

    job_ids = [row[0] for row in cur.fetchall()]   
    lines.append(f"JOB_ID possible values: {', '.join(job_ids)}")   

    cur = conn.execute(f"SELECT DISTINCT DEPARTMENT_ID FROM {TABLE_NAME} ORDER BY DEPARTMENT_ID")
    dept_ids = [str(row[0]) for row in cur.fetchall()]
    lines.append(f"DEPARTMENT_ID possible values: {', '.join(dept_ids)}")

    return "\n".join(lines)


if __name__ == "__main__":
    import sqlite3
    from load_data import load_csv_to_sqlite

    conn = sqlite3.connect(":memory:")
    load_csv_to_sqlite("employee_dataset.csv", conn)
    print(build_schema_description(conn))