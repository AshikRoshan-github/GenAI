import os
import re
import pandas as pd

def read_sql_file(file_path):
    with open(file_path, 'r', encoding='utf-16-le') as file:
        sql_query = file.read()
    return sql_query

def extract_table_and_columns(sql_query):
    pattern_table = r'CREATE\s+TABLE\s+\[\w+\]\.\[(.*?)\]'
    pattern_columns = r'CONSTRAINT \[.*?\] PRIMARY KEY .*?\((.*?)\)'
    pattern_timestamp = r'\[(.*?)\]\s*\[\s*(datetime|datetime2)\s*\]'
    
    table_match = re.findall(pattern_table, sql_query, re.IGNORECASE)
    table_name = table_match[0] if table_match else 'Unknown'

    columns_match = re.findall(pattern_columns, sql_query, re.DOTALL)
    columns = [col.strip().replace('[', '').replace(']', '').replace(' ASC', '') for col in columns_match[0].split(',')] if columns_match else []

    timestamp_matches = re.findall(pattern_timestamp, sql_query)
    timestamps = ', '.join([match[0] for match in timestamp_matches])

    return table_name, columns, timestamps

# Function to extract columns and their data types from the CREATE TABLE query
def extract_columns_and_datatypes(create_table_query):
    columns_and_datatypes = []

    # Pattern for columns with precision and scale
    pattern_with_precision_scale = r'\[(\w+)\]\s+\[(\w+)\]\s*\((\d+)(?:,\s*(\d+))?\)\s*(NOT\s+NULL|NULL)?'
    
    # Pattern for columns without precision and scale
    pattern_without_precision_scale = r'\[(\w+)\]\s+\[(\w+)\]\s*(NOT\s+NULL|NULL)?'
    
    # Check and match with both patterns
    matches_with_precision_scale = re.findall(pattern_with_precision_scale, create_table_query)
    matches_without_precision_scale = re.findall(pattern_without_precision_scale, create_table_query)
    
    for match in matches_with_precision_scale:
        column_name, data_type, precision, scale, nullability = match
        if precision and scale:
            full_data_type = f"{data_type}({precision},{scale})"
        else:
            full_data_type = f"{data_type}({precision})" if precision else data_type
        columns_and_datatypes.append((column_name, full_data_type))

    for match in matches_without_precision_scale:
        column_name, data_type, nullability = match
        full_data_type = data_type
        columns_and_datatypes.append((column_name, full_data_type))

    return columns_and_datatypes

def extract_size(data_type):
    # Find the positions of '(' and ')' in the data type string
    start = data_type.find('(')
    end = data_type.find(')')
    
    # If both '(' and ')' are found and in the correct order
    if start != -1 and end != -1 and start < end:
        size_str = data_type[start + 1:end]
        try:
            # Try converting the extracted substring to an integer
            return size_str
        except ValueError:
            # If conversion fails, return a default value or handle as needed
            return None
    else:
        # Return None or a default value if parentheses are not found
        return None

def is_primary_key(row):
    return 'TRUE' if (row['TableName'], row['ColumnName']) in primary_keys else ''

def is_timestamp_key(row):
    return 'TRUE' if (row['TableName'], row['ColumnName']) in Timestamp_cols else ''

# Directory containing your table scripts
table_scripts_dir = os.path.join(os.getcwd(),'Input_Floder','TableScript')

# Regular expression to match the table name
pattern = r'CREATE\s+TABLE\s+\[\w+\]\.\[(.*?)\]'

# List to store table information
table_info = []

# Get a list of all files in the directory
tables_list = os.listdir(table_scripts_dir)

for tables_list_item in tables_list:
    with open(os.path.join(table_scripts_dir, tables_list_item), 'r', encoding='utf-16-le') as file:
        create_table_query = file.read()
    columns_and_datatypes = extract_columns_and_datatypes(create_table_query)

    match = re.search(pattern, create_table_query)

    if match:
        table_name = match.group(1)
    else:
        table_name = "Unknown"

    for column, data_type in columns_and_datatypes:
        table_info.append([table_name, column, data_type])

# Create a DataFrame
df_Datatype = pd.DataFrame(table_info, columns=["TableName", "ColumnName", "DataType"])

df_Datatype = df_Datatype.drop_duplicates(subset=['TableName','ColumnName'])

df_Datatype['size'] = df_Datatype['DataType'].apply(extract_size)

df_Datatype['DataType'] = df_Datatype['DataType'].str.replace(r'\(\d+(,\d+)?\)', '', regex=True)

df_Datatype.to_csv(os.path.join(os.getcwd(),'Process_Folder', 'DataType.csv'),index=False)

primary_timestamp_data = []
table_primary_data = []
table_timestamp_data = []

for filename in os.listdir(table_scripts_dir):
    if filename.endswith('.sql'):
        file_path = os.path.join(table_scripts_dir, filename)
        sql_query = read_sql_file(file_path)
        table_name, columns, timestamps = extract_table_and_columns(sql_query)
        columns_main = ', '.join(columns)
        primary_timestamp_data.append((table_name, columns_main, timestamps))

df_Primarykey_Timestamp = pd.DataFrame(primary_timestamp_data, columns=['TableName', 'PrimaryKey', 'TimeStamp'])

for index, row in df_Primarykey_Timestamp.iterrows():
    table_name = row['TableName']
    primary_keys = [key.strip() for key in row['PrimaryKey'].split(',')]
    for key in primary_keys:
        table_primary_data.append({'TableName': table_name, 'PrimaryKey': key})

for index, row in df_Primarykey_Timestamp.iterrows():
    table_name = row['TableName']
    timestamp_keys = [key.strip() for key in row['TimeStamp'].split(',')]
    for key in timestamp_keys:
        table_timestamp_data.append({'TableName': table_name, 'TimeStamp': key})

df_primarykey = pd.DataFrame(table_primary_data)
df_timestamp = pd.DataFrame(table_timestamp_data)

primary_keys = df_primarykey.set_index(['TableName', 'PrimaryKey']).index
Timestamp_cols = df_timestamp.set_index(['TableName', 'TimeStamp']).index

df_Datatype['PrimaryKey'] = df_Datatype.apply(is_primary_key, axis=1)
df_Datatype['Timestamp'] = df_Datatype.apply(is_timestamp_key, axis=1)



df_Datatype.to_csv(os.path.join(os.getcwd(),'Process_Folder', 'Primarykey_Timestamp.csv'), index=False)
