# modules/text_processor.py
class TextProcessor:
    def __init__(self, filename):
        self.filename = filename

    def read_file_content(self):
        with open(self.filename, 'r') as file:
            content = file.read()
        return content
