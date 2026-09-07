import csv
import sqlite3
from datetime import datetime

#Parse column Functions
def parse_text(value):
    return value.strip()

def parse_int(value):
    return int(value.strip())

def parse_manager_id(value):
    stripped = value.strip()
    if stripped == 'NULL':
        return None
    return int(stripped)

def parse_hire_date(value):
    parsed_date = datetime.strptime(value.strip(), "%d-%b-%y")
    return parsed_date.strftime("%Y-%m-%d")

#SCHEMA
SCHEMA = [
    ("EMPLOYEE_ID", "INTEGER", parse_int),
    ("FIRST_NAME", "TEXT", parse_text),
    ("LAST_NAME", "TEXT", parse_text),
    ("EMAIL", "TEXT", parse_text),
    ("PHONE_NUMBER", "TEXT", parse_text),
    ("HIRE_DATE", "TEXT", parse_hire_date),
    ("JOB_ID", "TEXT", parse_text),
    ("SALARY", "INTEGER", parse_int),
    ("MANAGER_ID", "INTEGER", parse_manager_id),
    ("DEPARTMENT_ID", "INTEGER", parse_int)
]

TABLE_NAME = "employees" 

#Build table from schema

def build_create_table_sql():
    columns_sql = ",".join(f"{name} {sql_type}" for name, sql_type, _ in SCHEMA)
    return f"CREATE TABLE {TABLE_NAME} ({columns_sql})"

#Loader

def load_csv_to_sqlite(csv_path, conn):
    conn.execute(build_create_table_sql())

    column_names = [c for c, _, _ in SCHEMA]
    placeholders = ",".join("?" for _ in SCHEMA)

    insert_sql = f"INSERT INTO {TABLE_NAME} ({', '.join(column_names)}) VALUES ({placeholders})"


    with open(csv_path, newline="", encoding="utf-8") as f:
        file = csv.DictReader(f)

        for row in file:
            val = tuple(converter(row[name]) for name, _, converter in SCHEMA)
            conn.execute(insert_sql, val)
        
    conn.commit()

if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    load_csv_to_sqlite("employee_dataset.csv", conn)
    cur = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    print("Row count:", cur.fetchone()[0])
    cur = conn.execute(f"SELECT * FROM {TABLE_NAME} WHERE MANAGER_ID IS NULL")
    print("No manager:", cur.fetchall())