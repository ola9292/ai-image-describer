from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()
UPLOAD_FOLDER = './static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route("/")
def hello_world():
    return render_template('index.html')

def describe(name,length):
    with open(f'./static/images/{name}', 'rb') as f:
      image_bytes = f.read()

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
        types.Part.from_bytes(
            data=image_bytes,
            mime_type='image/jpeg',
        ),
        f'Describe this image in exactly one plain sentence with no formatting, bullets, or special characters. around and not more than {length} words. Do not use asterisks, bullets, or any markdown formatting.'
        ]
    )

    print(response.text)
    return response.text

@app.route('/process-image', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            # return redirect(request.url)
            print('no file')
        file = request.files['file']
        text_length = request.form.get('summary_length', 'short')
        print(text_length)

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            result = jsonify(describe(filename,text_length))
            return result 