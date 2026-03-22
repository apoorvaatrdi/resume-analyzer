from flask import Flask, render_template, request
import os
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Upload + Process Resume
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['resume']
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Extract text from PDF
        text = ""
        if file.filename.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()

        # Skill detection
        skills = ["python", "java", "c++", "sql", "html", "css", "javascript"]
        found_skills = []

        for skill in skills:
            if skill in text.lower():
                found_skills.append(skill)

        return render_template('result.html', text=text, skills=found_skills)

    return "No file uploaded"

if __name__ == '__main__':
    app.run(debug=True)