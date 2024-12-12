import pyodbc
import pandas as pd
import openai
import os
from dotenv import load_dotenv, find_dotenv

# Define database credentials (hidden for security)
server_name = 'your_server_name'
database_name = 'your_database_name'
user_id = 'your_user_id'
password = 'your_password'

# Define the connection string
connection_string = f'DRIVER={{SQL Server}};SERVER={server_name};DATABASE={database_name};UID={user_id};PWD={password}'

# Establish a connection to the database
try:
    conn = pyodbc.connect(connection_string)
except pyodbc.Error as e:
    print(f"Error connecting to the database: {e}")
    exit()

# Retrieving Column Names from the Database
# Define SQL query to retrieve column names
sql_query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'table_demo'"

# Use pandas to read data from the database
try:
    # Execute the SQL query and fetch results into a DataFrame
    df = pd.read_sql(sql_query, conn)
except pd.errors.DatabaseError as e:
    print(f"Error reading data from the database: {e}")
finally:
    # Close the database connection
    conn.close()

# Generating Column Comments with GPT-3.5
# Retrieve the API key from the environment variable
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # Control the randomness of the model's output
    )
    return response.choices[0].message["content"]

# Generate the prompt for GPT-3.5
column_values = df['COLUMN_NAME'].tolist()
prompt = f"""
Generate comments for the given list of column names: {column_values}.
Comments should be short and accurate as in the example: "Column_Name" -> "Stores the Column_Name."
Provide the output in python list format: ['comment1', 'comment2', ...].
"""

# Get response from GPT-3.5
response = get_completion(prompt)

# Process the response to extract comments
result_list = response[1:-1].split(',')
result_list = [element.strip().strip('"') for element in result_list]

# Combine column names with generated comments into a DataFrame
data = {
    "Column_Name": column_values,
    "Comment": result_list
}

df_comments = pd.DataFrame(data)

# Display the DataFrame with column names and comments
print(df_comments)
