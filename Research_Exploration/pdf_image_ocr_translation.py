from pdf2image import convert_from_path
import pytesseract
from googletrans import Translator

# Initialize the translator
translator = Translator()

# Convert PDF pages to images
pdf_path = r'D:\captcha\BL_Details_202405302045349658.pdf'
poppler_path = r"C:\Program Files\poppler-24.02.0\Library\bin"
pages = convert_from_path(pdf_path, poppler_path=poppler_path)

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\ashik.roshan\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Perform OCR on the first page, specifying both English and Arabic
text = pytesseract.image_to_string(pages[0], lang='eng+ara')
print(text)

# Translate the text to English
translation = translator.translate(text, src='ar', dest='en')

# # Print the translated text
print(translation.text)
