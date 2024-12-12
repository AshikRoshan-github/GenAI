import re
from modules.text_processor import TextProcessor

class MessageExtractor(TextProcessor):
    def __init__(self, filename):
        super().__init__(filename)

    def extract_error_messages(self):
        error_messages = []
        error_pattern1 = r"(raise_application_error\(\s*-\d+,\s*'([^']+)'\s*,\s*TRUE\s*\);)"
        error_pattern2 = r"(RAISE_APPLICATION_ERROR\(-\d+,'(.*?)'\);)"
        error_pattern3 = r"(raise_application_error\(-\d+, '(.+?)'\))"

        with open(self.filename, 'r') as file:
            for line in file:

                match1 = re.search(error_pattern1, line)
                
                if match1:
                    error_messages.append(match1.group(1))
                    
                match2 = re.search(error_pattern2, line)
                
                if match2:
                    error_messages.append(match2.group(1))
                
                match3 = re.search(error_pattern3, line)
                
                if match3:
                    error_messages.append(match3.group(1))

        return error_messages

    


    def extract_text(self, starting_str):
        ending_str = ";"
        pattern = re.compile(starting_str + r'(.*?)' + re.escape(ending_str), re.DOTALL | re.IGNORECASE)
        results = pattern.findall(self.read_file_content())
        return [msg[1].strip() for msg in results]
