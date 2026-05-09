import pandas as pd
import pyodbc
import psycopg2
import subprocess
import smtplib
from email.message import EmailMessage
from psycopg2.extras import execute_values
# Network credentials
PC_IP ="192.168.0.5"
PC_USERNAME = "santhosh"
PC_PASSWORD = "SM2706"
SHARED_FOLDER = "employee_poc"
FILE_NAME = "northwind.accdb"
#postgreSQL config
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "employee_db",
    "user": "postgres",
    "password": "Admin176"
}
#Email comnfig
EMAIL_SENDER = "santhoshsoffac@gmail.com"
EMAIL_PASSWORD = "mveexgnnefjrtsxc"
EMAIL_RECEIVER = "useranonymousan4@gmail.com"
def read_access_file():
    print("Authenticating to remote PC...")
    subprocess.run([
        "net", "use",
        f"\\\\{PC_IP}\\{SHARED_FOLDER}",
        PC_PASSWORD,
        f"/user:{PC_USERNAME}"
    ])
    print("Authentication successful")
    file_path = rf"\\{PC_IP}\{SHARED_FOLDER}\{FILE_NAME}"
    print(f"Accesssing file from: {file_path}")
    conn_str = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    f"DBQ=\\\\{PC_IP}\\{SHARED_FOLDER}\\{FILE_NAME};"
)
    conn = pyodbc.connect(conn_str)
    query = """
        SELECT
            ID,
            [First Name],
            [Last Name],
            [Job Title],
            [City],
            [Country/Region],
            [Business Phone]
            FROM Employees
    """
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"Read {len(df)} rows from Acess file")
    print(df)
    return df
def get_pg_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="employee_db",
        user="postgres",
        password="Admin176"
    )
    print("connected to postgreSQL")
    return conn
def create_table(pg_conn):
    create_sql = """
        CREATE TABLE IF NOT EXISTS northwind_employees (
            id INTEGER,
            first_name TEXT,
            last_name TEXT,
            job_title TEXT,
            city TEXT,
            country TEXT,
            business_phone TEXT,
            date DATE,
            in_time TIME,
            out_time TIME
            );
    """              
    cursor = pg_conn.cursor()
    cursor.execute(create_sql)
    pg_conn.commit()
    cursor.close()
    print("Table created successfully")
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
def add_attendance_columns(pg_conn):
    cursor = pg_conn.cursor()
    alter_queries = [
        'ALTER TABLE northwind_employees ADD COLUMN IF NOT EXISTS "date" DATE;',
        "ALTER TABLE northwind_employees ADD COLUMN IF NOT EXISTS in_time TIME;",
        "ALTER TABLE northwind_employees ADD COLUMN IF NOT EXISTS out_time TIME;"
    ]
    for query in alter_queries:
        cursor.execute(query)
    pg_conn.commit()
    cursor.close()
    print("Attendance columns added successfully!")
def insert_sample_attendance(pg_conn):
    cursor = pg_conn.cursor()
    update_sql = """
        UPDATE northwind_employees
        SET date = CURRENT_DATE,
            in_time = '10:15:00',
            out_time = '6:00:00'
        WHERE id = 1;
    """
    cursor.execute(update_sql)
    pg_conn.commit()
    cursor.close()
    print("Sample attendance data inserted successfully")
def check_and_notify_late(pg_conn):
    cursor = pg_conn.cursor()
    cursor.execute("""
        SELECT id, first_name, last_name, in_time, date
        FROM northwind_employees
        WHERE in_time > '10:00:00'
        AND date = CURRENT_DATE;
   """)
    late_employees = cursor.fetchall()
    if not late_employees:
        print("No late arrivals today")
        return
    for emp in late_employees:
        emp_id, first_name, last_name, in_time, date = emp

        msg = EmailMessage()
        msg['Subject'] = f'Late Arrival Alert - {first_name} {last_name}'
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg.set_content(f"""
Dear HR

This is an automated notification from Paragon Attendance Portal.
Employee {first_name} {last_name} (ID: {emp_id})
arrived late today ({date})
Check-in time: {in_time}

Regards,
Paragon Attendance Portal
        """)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Notification sent for {first_name} {last_name} (ID: {emp_id})")
        cursor.close()
def main():
    print("Starting sync process...\n")
    df = read_access_file()
    pg_conn = get_pg_connection()
    create_table(pg_conn)
    sync_to_postgres(df, pg_conn)
    add_attendance_columns(pg_conn)
    insert_sample_attendance(pg_conn)
    check_and_notify_late(pg_conn)
    pg_conn.close()
    print("\nAll done! Sync and attendance check completed succcessfully.")
if __name__ == "__main__":
    main()

                   