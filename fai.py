from fastapi import FastAPI
import psycopg2
#create fastapi app
app = FastAPI()
#connect to postgres
def get_pg_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="employee_db",
        user="postgres",
        password="Admin176"
    )
    return conn
#route 1
@app.get("/")
def home():
    return {"Message":"Welcome to the Employee API!"}
#route2
@app.get("/employees")
def get_employees():
    conn = get_pg_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM northwind_employees;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    employees = []
    for row in rows:
        employees.append({"id": row[0],
                     "first_name": row[1],
                     "last_name": row[2],
                     "job_title": row[3],
                     "city": row[4],
                     "country": row[5],
                     "business_phone": row[6]
        })
    return {"employees": employees}
#route3
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    conn = get_pg_connection()
    cursor = conn.cursor()
    print(f"Looking for employee id: {employee_id}")
    cursor.execute(
        "SELECT * FROM northwind_employees WHERE id = %s;", (employee_id,)
    )
    row = cursor.fetchone()
    print(f"Row found: {row}")
    cursor.close()
    conn.close()
    if row is None:
        return {"error":f"Employee {employee_id} not found"}
    return {
        "id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "job_title": row[3],
        "city": row[4],
        "country": row[5],
        "business_phone": row[6]
    }


                   
                   
