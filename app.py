from flask import Flask, request, jsonify
from flask_cors import CORS
from readability import Document
from lxml.html import fromstring
from resume import get_job_description_intern, get_job_description_normal, add_to_csv

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes

@app.route('/save-text', methods=['POST'])
def save_text():
    data = request.get_json()

    text = data.get('text', '').strip()
    html = data.get('html', '').strip()
    company_name = data.get('companyName', '').strip()
    company_link = data.get('companyLink', '').strip()
    resume_type = data.get('type', 'normal-resume')

    print(f"\n--- Incoming Request ---")
    print(f"Company Name: {company_name or 'N/A'}")
    print(f"Company Link: {company_link or 'N/A'}")
    print(f"Resume Type: {resume_type}")
    print(f"Text Present: {'Yes' if text else 'No'}")

    if not text and html:
        try:
            doc = Document(html)
            summary = doc.summary()
            text = fromstring(summary).text_content().strip()
        except Exception as e:
            print(f"HTML parsing failed: {e}")
            text = ''

    if not text:
        print("Text is empty. Adding job to CSV only.")
        add_to_csv(company_name, company_link)
        return jsonify(status="job added to CSV"), 200

    if resume_type == "normal-resume":
        rating = get_job_description_normal(text, company_name, company_link)
    elif resume_type == "intern-resume":
        rating = get_job_description_intern(text, company_name, company_link)
    else:
        print("Unknown resume type. Skipping.")
        return jsonify(status="invalid resume type"), 400

    return jsonify(status="processed successfully", rating=rating), 200

if __name__ == '__main__':
    app.run(port=5000)
