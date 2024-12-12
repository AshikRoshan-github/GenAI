import pandas as pd
import time
import os
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai
import subprocess

def get_description(table_name, column_name):
    desc_row = combined_mdd_df[
        (combined_mdd_df['Table Name'] == table_name) &
        (combined_mdd_df['Column Name'] == column_name)
    ]
    if not desc_row.empty:
        return desc_row['Description'].values[0]
    return None


primaryKey_size_timestamp_dir = os.path.join(os.getcwd(),'Python_Code','Primarykey_Size_Timestamp.py')

result = subprocess.run(['python', primaryKey_size_timestamp_dir ], capture_output=True, text=True)

print("Output:", result.stdout)
print("Errors:", result.stderr)
print("Return Code:", result.returncode)
# Load environment variables
load_dotenv()

# Configure the Google API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create the model
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 15000,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Start chat session
chat_session = model.start_chat(history=[])

# Define the path to the directory containing the table scripts
table_scripts_dir = os.path.join(os.getcwd(), 'Input_Floder', 'TableScript')

# Get a list of all files in the directory
tables_list = os.listdir(table_scripts_dir)


# Regex pattern to extract table name
pattern = r'CREATE\s+TABLE\s+\[\w+\]\.\[(.*?)\]'

dfs = []

# Initialize user_documents_dir
user_documents_dir = os.path.join(os.getcwd(), "Intermediate_Output_MetaData_Description")

# Process each table script file
for tables_list_item in tables_list:
    time.sleep(5)

    with open(os.path.join(table_scripts_dir, tables_list_item), 'r', encoding='utf-16-le') as file:
        create_table_query = file.read()

    match = re.search(pattern, create_table_query)

    if match:
        table_name = match.group(1)
        print("Table name extracted:", table_name)
    else:
        print("CREATE TABLE statement not found or invalid.")
        continue

    prompt_content = f"""

    #Schema:

        {create_table_query}

        
    #Sample_Response:

        {{
            "table": "{table_name}",
            "description": "xxxx",
            "columns": {{
                "columnname1": {{
                    "description": "yyyyy"
                }},
                "columnname2": {{
                    "description": "zzzzz"
                }}
            }}
        }}



    #Business Objective of the Waste Management Disposal Process:

    The waste management process starts with a customer generating waste from sources such as manufacturing facilities, hospitals, households, or any entity producing waste.\
    This waste is profiled to identify its type (industrial, medical, hazardous, or municipal solid waste), quantity, composition (e.g., plastics, metals, paper, chemicals),special handling requirements, and contamination levels.\
    Based on this profile, a price quote is provided, and a contract is negotiated outlining responsibilities, timelines, and payment terms. Specialized transporters are contracted to safely move the waste to a processing facility. \
    Upon arrival, the waste undergoes compliance and safety checks to meet regulatory standards, followed by weighing, sorting, and initial separation of large or hazardous items. If necessary, contaminants are removed to prepare the waste for treatment, ensuring it meets environmental regulations.\
    Detailed records of the washed waste are kept for traceability, and specific work orders are created for handling each type of waste. The treatment and processing stage involves batching similar waste materials, blending different types, and following precise procedures with reagents to transform the waste.\
    Depending on its composition and contamination levels, the waste may undergo composting, anaerobic digestion, incineration, or other technologies like pyrolysis or chemical treatment. Valuable by-products are collected, tracked, and stored separately for sale or reuse. \
    For disposal, non-treatable waste is transported to licensed landfills, with non-hazardous waste going to regular landfills and hazardous waste handled with specialized procedures. Various processes like solidification, stabilization, neutralization, propylene glycol distillation, aerosol recycling, and thermal desorption are employed as needed.\
    Waste may also be shipped offsite to specialized facilities, ensuring compliance with safety and regulations. Administrative and financial aspects include processing costs for receiving, sorting, and preparing waste, treatment costs for specific methods, transportation costs, and disposal costs in licensed facilities.\
    Revenue can be generated from selling by-products, reducing overall waste management costs. Product sales invoicing and empty container tracking ensure proper handling, return, and reuse of containers and equipment.

    #note:

    Generate a description based on the Business Objective of the Waste Management Disposal Process.

    #Prompt:

    From the provided SQL schema of the table query, generate an detailed metadata descriptions for the table and each columns. \
    Provide detailed and elaborated descriptions for each column in the table, focusing on the business objectives and context.\
    Do not specify the datatype in column descriptions Which should be adhered to strictly.\
    Return the response as a structured JSON object and do not stop generating the response till all columns are given descriptions.
    """

    response = chat_session.send_message(prompt_content)

    json_input = response.text
    print(json_input)

    final_result = json_input.replace("```", "").replace("json", "")

    # Create directories if they don't exist
    json_file_path = os.path.join(user_documents_dir, "MetadataDescription_Proper_Json", f"{table_name}.txt")
    improper_json_file_path = os.path.join(user_documents_dir, "MetadataDescription_Improper_Json", f"{table_name}.txt")
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    os.makedirs(os.path.dirname(improper_json_file_path), exist_ok=True)

    # Write the result to the appropriate file
    try:
        data = json.loads(final_result)
        table_name = data['table']
        table_description = data['description']
        columns_data = data['columns']

        columns_list = [
                    {'Table Name': table_name, 'Table Description': table_description, 'Column Name': col, 'Description': columns_data[col]['description']}
                    for col in columns_data
                ]

        df_result = pd.DataFrame(columns_list)
        dfs.append(df_result)

        with open(json_file_path, 'w') as file:
             file.write(json_input + '\n' + "----------------------------------------------------------" + '\n')

    except json.JSONDecodeError as e:
        
        print(f"JSON decode error for {table_name}: {e}")

        with open(improper_json_file_path, 'w') as file:
            file.write(final_result + '\n' + "----------------------------------------------------------" + '\n')

        continue

combined_mdd_df = pd.concat(dfs, ignore_index=True)

combined_mdd_df.to_csv(os.path.join(os.getcwd(),'Process_Folder', 'Combined_MDD.csv'),index=False)

PST_DF = pd.read_csv(os.path.join(os.getcwd(),'Process_Folder', 'Primarykey_Timestamp.csv'))

PST_DF['Description'] = PST_DF.apply(lambda row: get_description(row['TableName'], row['ColumnName']), axis=1)

PST_DF.to_csv(os.path.join(os.getcwd(),'Final_Collect_Area','MetaData_Description_Columns.csv'),index=False)

TTD_DF = combined_mdd_df[['Table Name', 'Table Description']]

TTD_DF = TTD_DF.drop_duplicates()

TTD_DF.to_csv(os.path.join(os.getcwd(), 'Final_Collect_Area', 'MetaData_Description_Tables.csv'), index=False)
