from flask import Flask, request, render_template
import fitz  # PyMuPDF
import os
import google.generativeai as genai
from dotenv import load_dotenv

# ==========================
# Load Environment Variables
# ==========================
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

# ==========================
# Gemini Model
# ==========================
model = genai.GenerativeModel("gemini-1.5-flash-8b")

# ==========================
# Flask Setup
# ==========================
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ==========================
# Extract Text from PDF
# ==========================
def extract_text_from_pdf(pdf_path):
    text = ""

    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()

    except Exception as e:
        print("PDF Error:", e)

    return text

# ==========================
# Home Route
# ==========================
@app.route("/", methods=["GET", "POST"])
def index():

    analysis_result = None

    if request.method == "POST":

        file = request.files.get("resume")
        job_description = request.form.get("job_description", "")

        if not file:
            return render_template(
                "index.html",
                analysis_result="Please upload a resume."
            )

        if not file.filename.lower().endswith(".pdf"):
            return render_template(
                "index.html",
                analysis_result="Only PDF files are supported."
            )

        try:

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            resume_text = extract_text_from_pdf(filepath)

            prompt = f"""
You are an advanced ATS Resume Analyzer.

Analyze the resume against the job description.

Return the result in the following format:

# Parsed Resume Information

Name:
Email:
Phone:
Skills:
Education:
Work Experience:
Certifications:

# ATS Match Analysis

Match Score: X/100

Explanation:
(Explain why the score was given)

# Missing Skills

(List important missing skills if any)

# Resume Improvement Suggestions

(Provide detailed suggestions)

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}
"""

            response = model.generate_content(prompt)

            analysis_result = response.text

        except Exception as e:

            analysis_result = f"""
Gemini Error:

{str(e)}

Possible Reasons:
- Gemini quota exhausted
- Invalid API key
- Network issue
- Temporary Gemini outage
"""

    return render_template(
        "index.html",
        analysis_result=analysis_result
    )

# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    app.run(debug=True)