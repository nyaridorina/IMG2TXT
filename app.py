from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
import os

# Initialize Flask app
app = Flask(__name__)

# Specify the path to the tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\dnyari\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'  # Adjust this path for your system

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
            return 'No file part'
        file = request.files['file']
        # If the user does not select a file, the browser might submit an empty part
        if file.filename == '':
            return 'No selected file'
        if file:
            # Save the file to the upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            # Extract text using Tesseract OCR
            extracted_text = extract_text(file_path)
            return render_template('result.html', text=extracted_text)
    return render_template('index.html')

# Function to extract text from an image using pytesseract
def extract_text(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

@app.errorhandler(500)
def internal_error(error):
    return "An internal server error occurred: {}".format(error), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
