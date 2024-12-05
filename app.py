from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
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
            # Extract text using OCR
            try:
                extracted_text = extract_text_from_image(file_path)
                return render_template('result.html', text=extracted_text)
            except Exception as e:
                app.logger.error(f"Error processing file: {str(e)}")
                return render_template('index.html', error="Error processing the file")
    return render_template('index.html')

# Function to extract text from images
def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        # Format the text line by line
        formatted_text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
        return formatted_text
    except Exception as e:
        app.logger.error(f"Error extracting text: {str(e)}")
        raise e

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"An internal server error occurred: {str(error)}")
    return "An internal server error occurred: {}".format(error), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
