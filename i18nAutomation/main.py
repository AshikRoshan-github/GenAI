import os
import csv
import pandas as pd
import streamlit as st
from modules.procedure_extractor import ProcedureExtractor
from modules.error_message_analyzer import ErrorMessageAnalyzer

def save_file(content, file_path):
    # Decode the byte content into a string
    decoded_content = content.decode("utf-8")
    # Write the decoded content to the file
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(decoded_content)


def replace_csv_content(uploaded_file_csv, existing_csv_path):
    if os.path.isfile(existing_csv_path):
        # Write the uploaded DataFrame to the CSV file, replacing existing content
        uploaded_file_csv.to_csv(existing_csv_path, index=False)


def main():

    folder_path = r"D:\AUTOMATING_TYLER_PROJECT\separated_procedure_txt_files"

    # List all files in the folder
    files = os.listdir(folder_path)

    # Loop through the files and delete each one
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    st.title("Internationlization")

    uploaded_file = st.file_uploader("Upload a txt file", type=["txt"])

    if uploaded_file is not None:
        content = uploaded_file.read()
        file_path = r'D:\AUTOMATING_TYLER_PROJECT\source_txt_sql_file\Internationalization (1).txt'
        save_file(content, file_path)

    uploaded_file_csv = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file_csv is not None:
        # Read the uploaded CSV file
        uploaded_df = pd.read_csv(uploaded_file_csv, delimiter=',', quoting=csv.QUOTE_NONE, names=['Tables', 'Columns', 'DataType'])
          # Display the uploaded DataFrame

        # Specify the path to the existing CSV file
        existing_csv_path = r"D:\AUTOMATING_TYLER_PROJECT\source_txt_sql_file\schem_csv.csv"

        # Replace the content of the existing CSV file with the uploaded data
        replace_csv_content(uploaded_df, existing_csv_path)

    file_path = r'D:\AUTOMATING_TYLER_PROJECT\source_txt_sql_file\Internationalization (1).txt'
    procedure_extractor = ProcedureExtractor(file_path)
    procedure_extractor.extract_procedure()

    directory = r'D:\AUTOMATING_TYLER_PROJECT\separated_procedure_txt_files'
    error_message_analyzer = ErrorMessageAnalyzer(directory)
    concatenated_list = error_message_analyzer.analyze_messages()   

    schema_path_file = r'D:\AUTOMATING_TYLER_PROJECT\source_txt_sql_file\schem_csv.csv'
    col_row_value = error_message_analyzer.analyze_schema_file(concatenated_list,schema_path_file)

   


    data = {
        "Messages": concatenated_list,
        "Value_appended_Messages": col_row_value
        }

    df = pd.DataFrame(data)


    excel_file_path = r"D:\AUTOMATING_TYLER_PROJECT\excel_file\final_output.xlsx"

# Save DataFrame to Excel file
    df.to_excel(excel_file_path, index=False)
    
    st.write(df)
# Display a download button to download the Excel file
    st.download_button(
        label="Download excel file",
        data=open(excel_file_path, 'rb'),  # Open the Excel file in binary mode
        file_name='final_output.xlsx',
     mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
     )
    


if __name__ == "__main__":
    main()
