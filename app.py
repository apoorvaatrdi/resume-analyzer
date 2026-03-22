import os
import openai
from flask import Flask, render_template, request, send_file
import docx2txt
from io import BytesIO
from fpdf import FPDF  # for PDF download

app = Flask(__name__)

# OpenAI API key (use environment variable for deployment)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# List of skills to detect
SKILLS = ["python", "java", "c++", "sql", "html", "css", "javascript", "django", "flask"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['resume']
    if not file or file.filename == '':
        return "No file selected"

    text = docx2txt.process(file)
    text_lower = text.lower()

    # Detect skills
    found_skills = [skill for skill in SKILLS if skill in text_lower]

    # Resume Score
    score = min(len(found_skills) * 10, 100)

    # AI Suggestions (with fallback if OpenAI fails)
    suggestions = []
    try:
        prompt = f"Resume text:\n{text}\nDetected skills: {found_skills}\nProvide 3 actionable suggestions for improving this resume."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        ai_suggestions = response['choices'][0]['message']['content'].split("\n")
        suggestions = [s.strip("-• ") for s in ai_suggestions if s.strip()]
    except:
        # Fallback suggestions if OpenAI API fails or key is missing
        if "python" not in found_skills:
            suggestions.append("Learn Python for better opportunities")
        if "sql" not in found_skills:
            suggestions.append("Add SQL skills for data-related roles")
        if "projects" not in text.lower():
            suggestions.append("Add a projects section in your resume")
        if len(found_skills) < 3:
            suggestions.append("Try to add more technical skills")
        if not suggestions:
            suggestions.append("Add more details to improve your resume")

    return render_template('result.html', text=text, skills=found_skills, score=score, suggestions=suggestions)

@app.route('/download', methods=['POST'])
def download_pdf():
    text = request.form['text']
    skills = request.form.getlist('skills')
    suggestions = request.form.getlist('suggestions')
    score = request.form['score']

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Resume Analysis Result - Score: {score}/100", ln=1)
    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.cell(0, 10, "Detected Skills:", ln=1)
    for s in skills:
        pdf.cell(0, 10, f"- {s}", ln=1)
    pdf.ln(3)
    pdf.cell(0, 10, "Suggestions:", ln=1)
    for s in suggestions:
        pdf.cell(0, 10, f"- {s}", ln=1)
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Full Resume Text:\n" + text)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return send_file(pdf_output, download_name="Resume_Analysis.pdf", as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Works locally and on Render
    app.run(debug=True, host='0.0.0.0', port=port)