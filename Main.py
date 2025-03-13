import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import PyPDF2
import openai

# Load environment variables
load_dotenv()

# Initialize Flask and OpenAI
app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads'
openai.api_key = os.environ["OPENAI_API_KEY"]

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_summary(text):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes research papers."},
            {"role": "user", "content": f"Please summarize this research paper: {text}"}
        ]
    )
    return response.choices[0].message.content

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded'
        file = request.files['file']
        if file.filename == '':
            return 'No file selected'
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text and get summary
            text = extract_text_from_pdf(filepath)
            summary = get_summary(text)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return render_template('result.html', summary=summary)
    return render_template('upload.html')

if __name__ == "__main__":
    app.run(debug=True)
