import os
import re
import pandas as pd
import csv
from modules.message_extractor import MessageExtractor

class ErrorMessageAnalyzer:
    def __init__(self, directory):
        self.directory = directory

    def analyze_messages(self):
        
        all_error_messages = []
        
        
        all_o_messages = []
        all_v_messages = []
        
        all_o_errmsg = []
        all_v_errmsg = []


        for filename in os.listdir(self.directory):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.directory, filename)
                message_extractor = MessageExtractor(file_path)
                error_messages = message_extractor.extract_error_messages()
                

                o_messages = message_extractor.extract_text(r"(o_MSG\s*:=\s*'|o_msg\s*:=\s*')")
                v_messages = message_extractor.extract_text(r"(v_MSG\s*:=\s*'|v_msg\s*:=\s*')")
                  
                o_errmsg_messages = message_extractor.extract_text(r"(o_errmsg\s*:=\s*'|o_ERRMSG\s*:=\s*')")
                v_errmsg_messages = message_extractor.extract_text(r"(v_errmsg\s*:=\s*'|v_ERRMSG\s*:=\s*')")
                  
                all_error_messages.extend(error_messages)
                
             
                all_o_messages.extend(o_messages)
                all_v_messages.extend(v_messages)
                all_o_errmsg.extend(o_errmsg_messages)
                all_v_errmsg.extend(v_errmsg_messages)

        concatenated_list = all_error_messages + all_o_messages + all_v_messages + all_o_errmsg + all_v_errmsg

        cleaned_messages = [msg.replace("\n", "").replace("                 ", "").replace("          ", "") for msg in concatenated_list]
        
        values_to_remove = ["'", "COMDAT (CA31)'", "DWELDAT (CA21)'","ERROR - '||SQLERRM", "ERR:' || SQLERRM"]

        cleaned_messages = [item for item in cleaned_messages if item not in values_to_remove]


        return cleaned_messages

    def analyze_schema_file(self, concatenated_list,schema_path_file):
        col_row_value = []

        # Load schema CSV file
        df = pd.read_csv(schema_path_file, delimiter=',', quoting=csv.QUOTE_NONE, names=['Tables', 'Columns', 'DataType'])
        
        # Extract table and column names
        Table_names = [x.strip('"') for x in df['Tables'].tolist()]
        Column_names = [x.strip('"') for x in df['Columns'].tolist()]

        # Iterate over the error messages
        for msg in concatenated_list:
            output_string = msg

            # Find all words in the input string
            splited_string = re.findall(r'\w+', output_string)

            # Iterate over the words in the input string
            for word in splited_string:
                # Check if the word matches any table name
                if word.upper() in map(str.upper, Table_names):
                    # Replace the matched table name with a placeholder
                    output_string = re.sub(r'\b{}\b'.format(re.escape(word)), "{table_name}", output_string)

                # Check if the word matches any column name
                if word.upper() in map(str.upper, Column_names):
                    if word.upper() == 'ID' and splited_string[0] == 'Invalid':
                        pass
                    else:
                        output_string = re.sub(r'\b{}\b'.format(re.escape(word)), "{column_name}", output_string)

            col_row_value.append(output_string)

        return col_row_value
