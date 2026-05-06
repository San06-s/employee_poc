import pandas as pd

# Creating fake employee data
data = {
    "employee_id": [1, 2, 3, 4, 5],
    "name": ["John", "Paul", "Ravi", "Shaik", "Arjun"],
    "location": ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad"],
    "experience": [3, 5, 2, 7, 4]
}

# Converting that data into a DataFrame (like a table)
df = pd.DataFrame(data)

# Saving it as a CSV file
df.to_csv("employees.csv", index=False)

print("CSV file created successfully!")
print(df)
      