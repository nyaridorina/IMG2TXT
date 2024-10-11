from flask import Flask, render_template, request, redirect, url_for
import requests
from PIL import Image
import os

# Initialize Flask app
app = Flask(__name__)

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
            # Extract text using an OCR API
            extracted_text = extract_text(file_path)
            return render_template('result.html', text=extracted_text.replace('\n', '<br>'))
    return render_template('index.html')

# Function to extract text from an image using OCR API
def extract_text(image_path):
    try:
        api_key = 'K82639348088957'  # Replace with your actual API key
        with open(image_path, 'rb') as file:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                files={'file': file},
                data={'apikey': api_key}
            )
        result = response.json()
        return result.get("ParsedResults")[0].get("ParsedText").replace('\n', '\n') if result.get("ParsedResults") else "No text found"
    except Exception as e:
        return f"Error extracting text: {str(e)}"

@app.errorhandler(500)
def internal_error(error):
    return "An internal server error occurred: {}".format(error), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
