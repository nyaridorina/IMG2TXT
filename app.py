from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import fitz  # PyMuPDF for handling PDFs
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='error.log', level=logging.DEBUG)

# Set the upload folder
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route for home page
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', error="No file part")
        file = request.files['file']
        # If the user does not select a file, the browser might submit an empty part
        if file.filename == '':
            return render_template('index.html', error="No selected file")
        if file:
            # Save the file to the upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(file_path)
            # Extract table text
            try:
                extracted_text = extract_table(file_path)
                return render_template('result.html', text=extracted_text)
            except Exception as e:
                app.logger.error(f"Error processing file: {str(e)}")
                return render_template('index.html', error="Error processing the file")
    return render_template('index.html')

# Function to extract tables from image or PDF
def extract_table(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        # Process image file
        return extract_table_from_image(file_path)
    elif ext == '.pdf':
        # Process PDF file
        return extract_table_from_pdf(file_path)
    else:
        raise ValueError("Unsupported file type")

# Function to extract tables from images
def extract_table_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, config='--psm 6')  # PSM 6 assumes a single uniform block of text
        return format_table_text(text)
    except Exception as e:
        app.logger.error(f"Error extracting table from image: {str(e)}")
        raise e

# Function to extract tables from PDFs
def extract_table_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return format_table_text(text)
    except Exception as e:
        app.logger.error(f"Error extracting table from PDF: {str(e)}")
        raise e

# Format extracted text line by line
def format_table_text(text):
    lines = text.splitlines()
    formatted_text = '\n'.join(line.strip() for line in lines if line.strip())
    return formatted_text

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"An internal server error occurred: {str(error)}")
    return "An internal server error occurred: {}".format(error), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
