from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import logging
import pandas as pd

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
            # Extract table from the image
            try:
                table_html = extract_table_from_image(file_path)
                return render_template('result.html', table_html=table_html)
            except Exception as e:
                app.logger.error(f"Error processing file: {str(e)}")
                return render_template('index.html', error="Error processing the file")
    return render_template('index.html')

# Function to extract table from images and format as HTML table
def extract_table_from_image(image_path):
    try:
        img = Image.open(image_path)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DATAFRAME)

        # Filter out rows with no text
        data = data[data['text'].notnull()]

        # Reconstruct table based on `block_num`, `par_num`, and `line_num`
        table_data = []
        current_row = []
        last_line_num = None

        for _, row in data.iterrows():
            if last_line_num is not None and row['line_num'] != last_line_num:
                # Add the current row to the table and start a new row
                table_data.append(current_row)
                current_row = []
            current_row.append(row['text'])
            last_line_num = row['line_num']

        # Append the last row
        if current_row:
            table_data.append(current_row)

        # Convert table data into an HTML table
        table_html = pd.DataFrame(table_data).to_html(index=False, header=False, escape=False)
        return table_html
    except Exception as e:
        app.logger.error(f"Error extracting table from image: {str(e)}")
        raise e

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"An internal server error occurred: {str(error)}")
    return "An internal server error occurred: {}".format(error), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
