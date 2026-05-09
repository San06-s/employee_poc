import pandas as pd
import pyodbc
import psycopg2
import subprocess
from psycopg2.extras import execute_values
# Network credentials
PC_IP = "192.168.5.141"          
PC_USERNAME = "jarvis"   
PC_PASSWORD = "SM2706"    
SHARED_FOLDER = "employee_poc"    
FILE_NAME = "northwind.accdb"     
# PostgreSQL config
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "employee_db",
    "user": "postgres",
    "password": "Admin176"
}
def read_access_file():
    print("Authenticating to remote PC...")
    subprocess.run([
        "net", "use",
        f"\\\\{PC_IP}\\{SHARED_FOLDER}",
        PC_PASSWORD,
        f"/user:{PC_USERNAME}"
    ])
    print("Authentication successful!")
#network file path
    file_path = rf"\\{PC_IP}\{SHARED_FOLDER}\{FILE_NAME}"
    print(f"Accessing file from: {file_path}")
#connect to access file
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={file_path};"
    )
    conn = pyodbc.connect(conn_str)
    query = """
        SELECT
            ID,
            [First Name],
            [Last Name],
            [Job Title],
            City,
            [Country/Region],
            [Business Phone]
        FROM Employees
    """
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"Read {len(df)} rows from Access file")
    print(df)
    return df
#connect to postgres
def get_pg_connection():                        
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="employee_db",
        user="postgres",
        password="Admin176"
    )
    print("Connected to PostgreSQL!")
    return conn
#create table
def create_table(pg_conn):                      # ← SAME!
    create_sql = """
        CREATE TABLE IF NOT EXISTS northwind_employees (
            id              INTEGER,
            first_name      TEXT,
            last_name       TEXT,
            job_title       TEXT,
            city            TEXT,
            country         TEXT,
            business_phone  TEXT
        );
    """
    cursor = pg_conn.cursor()
    cursor.execute(create_sql)
    pg_conn.commit()
    cursor.close()
    print("Table created in PostgreSQL!")
#sync
def sync_to_postgres(df, pg_conn):             
    cursor = pg_conn.cursor()
    cursor.execute("DELETE FROM northwind_employees;")
    values = [tuple(row) for row in df.itertuples(index=False, name=None)]
    insert_sql = """
        INSERT INTO northwind_employees
        (id, first_name, last_name, job_title, city, country, business_phone)
        VALUES %s
    """
    execute_values(cursor, insert_sql, values)
    pg_conn.commit()
    cursor.close()
    print(f"Synced {len(df)} rows to PostgreSQL!")
#main
def main():
    print("Starting sync process...\n")
    df = read_access_file()             
    pg_conn = get_pg_connection()
    create_table(pg_conn)
    sync_to_postgres(df, pg_conn)
    pg_conn.close()
    print("\nSync completed successfully!")

if __name__ == "__main__":
    main()




