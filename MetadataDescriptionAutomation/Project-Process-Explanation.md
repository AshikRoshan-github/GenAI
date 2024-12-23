The process you've described extracts schema information from SQL files, generates metadata descriptions using a large language model (LLM), and combines this information into final output files. Here's a breakdown of the architecture at a high level:

1. Schema Extraction and Pre-processing:

Input: SQL files containing CREATE TABLE statements located in the "Input_Folder/TableScript" directory.

Process:

The code iterates through each SQL file.

It extracts the table name, column names, data types, primary keys, and timestamps using regular expressions.

It also extracts size information from data types and cleans the data type strings.

This extracted information is stored in Pandas DataFrames.

Output:

"Process_Folder/DataType.csv": Contains table name, column name, data type, and size.

"Process_Folder/Primarykey_Timestamp.csv": Contains table name, column name, primary key indicator, and timestamp indicator.

2. Metadata Description Generation:

Input:

"Input_Folder/TableScript": SQL files (same as previous stage).

Business Objective Prompt: A predefined prompt providing context for the LLM.

Process:

The code iterates through each SQL file.

It extracts the table name using regex.

It constructs a prompt for the LLM. The prompt includes:

The CREATE TABLE statement (schema).

A sample JSON response format.

The Business Objective prompt.

Instructions for generating descriptions.

It sends the prompt to the Google Gemini LLM.

It parses the JSON response from the LLM, extracting table and column descriptions.

Handles potential JSON decoding errors.

Output:

"Intermediate_Output_MetaData_Description/MetadataDescription_Proper_Json/*.txt": Files containing valid JSON responses from the LLM, one per table.

"Intermediate_Output_MetaData_Description/MetadataDescription_Improper_Json/*.txt": Files containing invalid JSON responses (if any).

"Process_Folder/Combined_MDD.csv": Consolidated CSV file containing table names, table descriptions, column names, and column descriptions.

3. Combining and Final Output:

Input:

"Process_Folder/Primarykey_Timestamp.csv": From stage 1.

"Process_Folder/Combined_MDD.csv": From stage 2.

Process:

The code merges the data from the two input CSV files based on table and column names. This adds the descriptions to the primary key/timestamp information.

It creates a separate CSV file for table-level descriptions.

Output:

"Final_Collect_Area/MetaData_Description_Columns.csv": Final CSV with column-level information, including primary key, timestamp, data type, and description.

"Final_Collect_Area/MetaData_Description_Tables.csv": Final CSV with table-level descriptions.

Architecture Diagram (Simplified):

![image](https://github.com/user-attachments/assets/cdd09943-8bd5-4c6e-a463-f8edfd3dd824)
