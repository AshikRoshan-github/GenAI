from modules.text_processor import TextProcessor
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class ProcedureExtractor(TextProcessor):
    def __init__(self, filename):
        super().__init__(filename)

    def extract_procedure(self):
        notepad_content = self.read_file_content()
        r_splitter = RecursiveCharacterTextSplitter(separators=['PROCEDURE'], chunk_size=100, chunk_overlap=0)
        chunked_content = r_splitter.split_text(notepad_content)
        
        for i, chunk in enumerate(chunked_content):
            with open(f"D:\\AUTOMATING_TYLER_PROJECT\\separated_procedure_txt_files\\procedure_{i}.txt", "w") as file:
                file.write(chunk)         
