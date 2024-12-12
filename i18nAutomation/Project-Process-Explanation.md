PL/SQL-internationalization:

The code implements a process for extracting and analyzing error messages from PL/SQL procedures and enriching them with schema information. Here's a breakdown of the architecture:

1. File Upload and Replacement (Streamlit):

Input: User uploads a .txt file (PL/SQL procedures) and a .csv file (schema information) via the Streamlit interface.

Process:

The uploaded .txt file's content is saved to a predefined location (D:\AUTOMATING_TYLER_PROJECT\source_txt_sql_file\Internationalization (1).txt).

The uploaded .csv file's content replaces the content of an existing CSV file (D:\AUTOMATING_TYLER_PROJECT\source_txt_sql_file\schem_csv.csv).

Output: Updated files on the local disk.

2. Procedure Extraction:

Input: The saved PL/SQL procedure file (Internationalization (1).txt).

Process:

The ProcedureExtractor class uses RecursiveCharacterTextSplitter from langchain to split the content into individual procedures based on the PROCEDURE keyword.

Output: Multiple .txt files, each containing a single procedure, saved in the D:\AUTOMATING_TYLER_PROJECT\separated_procedure_txt_files directory.

3. Error Message Analysis:

Input: The directory containing the separated procedure files.

Process:

The ErrorMessageAnalyzer class iterates through each procedure file.

The MessageExtractor class extracts error messages using regular expressions that match raise_application_error calls and custom message variables (o_MSG, v_MSG, o_errmsg, v_errmsg).

Extracted messages are cleaned (newline characters, extra spaces, specific strings removed).

Output: A list of cleaned error messages (concatenated_list).

4. Schema Enrichment:

Input:

The list of cleaned error messages (concatenated_list).

The schema CSV file (schem_csv.csv).

Process:

The analyze_schema_file method in ErrorMessageAnalyzer reads the schema CSV.

It iterates through the error messages and replaces table and column names found in the messages with placeholders ({table_name}, {column_name}). This is done using regular expressions and lookups against the schema CSV.

Output: A list of error messages enriched with table/column placeholders (col_row_value).

5. Output to Excel and Streamlit:

Input:

The original list of error messages (concatenated_list).

The schema-enriched error messages (col_row_value).

Process:

A Pandas DataFrame is created from the two lists.

The DataFrame is saved to an Excel file (D:\AUTOMATING_TYLER_PROJECT\excel_file\final_output.xlsx).

The DataFrame is also displayed in the Streamlit application.

A download button for the Excel file is provided in the Streamlit interface.

Output: Excel file and Streamlit display of the results.

Architecture Diagram (Simplified):

![image](https://github.com/user-attachments/assets/6b1fdc4e-01b8-4d74-b4ec-7b565d9d0e9b)

HTML-internationalization:
