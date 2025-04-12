from flask import Flask, request, render_template, redirect
import fitz  # PyMuPDF
import os
import google.generativeai as genai

# === Configure Gemini ===
genai.configure(api_key="AIzaSyD79HO4ZaERC1etXA7YSMpZNkouhkvS2I8")

model = genai.GenerativeModel("models/gemini-1.5-pro-002")

# === Flask Setup ===
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Helper Function to Extract Text ===
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# === Route: Home Page ===
@app.route("/", methods=["GET", "POST"])
def index():
    parsed_data = None
    match_score = None
    feedback = None

    if request.method == "POST":
        file = request.files["resume"]
        job_description = request.form["job_description"]

        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            resume_text = extract_text_from_pdf(filename)

            # Step 1: Extract structured resume data
            extract_prompt = f"""
You are an AI resume parser. Extract the following details in JSON format:
- Name
- Email
- Phone
- Skills
- Education
- Work Experience
- Certifications

Resume:
{resume_text}
"""
            parsed_response = model.generate_content([extract_prompt])
            parsed_data = parsed_response.text

            # Step 2: Match with Job Description
            match_prompt = f"""
Given the resume and job description, provide:
1. Match Score (0-100)
2. Short Explanation of the match

Resume:
{resume_text}

Job Description:
{job_description}
"""
            match_response = model.generate_content([match_prompt])
            match_score = match_response.text

            # Step 3: Give feedback
            feedback_prompt = f"""
Provide feedback on how the following resume can be improved:
{resume_text}
"""
            feedback_response = model.generate_content([feedback_prompt])
            feedback = feedback_response.text

    return render_template("index.html", parsed_data=parsed_data, match_score=match_score, feedback=feedback)

if __name__ == "__main__":
    app.run(debug=True)
