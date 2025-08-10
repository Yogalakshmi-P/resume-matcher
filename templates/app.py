from flask import Flask, render_template, request, jsonify
import fitz  # PyMuPDF
import string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Full stopwords set
stopwords = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
    'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
    'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
    'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren',
    "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't",
    'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't",
    'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        page_text = page.get_text()
        if page_text:
            text += page_text + " "
    return text.strip()

def extract_keywords(text):
    text = text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    return set(word for word in words if word not in stopwords)

def match_resume_to_jd(jd_text, resume_text):
    jd_keywords = extract_keywords(jd_text)
    resume_keywords = extract_keywords(resume_text)
    common = jd_keywords.intersection(resume_keywords)
    if not jd_keywords:
        return 0, set()
    percentage = (len(common) / len(jd_keywords)) * 100
    return round(percentage, 2), common

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/match', methods=['POST'])
def match():
    jd_file = request.files.get('jd_file')
    resume_file = request.files.get('resume_file')

    if not jd_file or not resume_file:
        return jsonify({"error": "Missing files"}), 400

    # Secure filenames to avoid issues
    jd_filename = secure_filename(jd_file.filename)
    resume_filename = secure_filename(resume_file.filename)

    jd_path = os.path.join(UPLOAD_FOLDER, jd_filename)
    resume_path = os.path.join(UPLOAD_FOLDER, resume_filename)

    jd_file.save(jd_path)
    resume_file.save(resume_path)

    jd_text = extract_text_from_pdf(jd_path)
    resume_text = extract_text_from_pdf(resume_path)

    match_percent, matched_keywords = match_resume_to_jd(jd_text, resume_text)

    return jsonify({
        "match_percent": match_percent,
        "matched_keywords": sorted(list(matched_keywords))
    })

if __name__ == '__main__':
    app.run(debug=True)
