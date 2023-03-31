import io
import os

import openai
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import documentai
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = "uploads"

ALLOWED_EXTENSIONS = set(["pdf"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def summarize_text(text):
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful asistant"},
                {"role": "user", "content": f"summarize this text in Japanese, within 300 characters: {text}"},
                ]
            )
    return response.choices[0]['message']['content']

def process_pdf(project_id, location, processor_id, file_path):
    client = documentai.DocumentProcessorServiceClient()

    name = client.processor_path(project_id, location, processor_id)

    with open(file_path, "rb") as image:
        image_content = image.read()
        raw_document = documentai.RawDocument(content=image_content, mime_type="application/pdf")

        # request_ = {"name": name, "document": document}
        request_ = documentai.ProcessRequest(name=name, raw_document=raw_document)
        result = client.process_document(request=request_)

        # Extract and return the text from the document
        return result.document.text


@app.route('/upload', methods=['POST'])
def upload_file():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if 'file' not in request.files:
        return jsonify({"message": "ファイルがありません"}), 400

    file = request.files.get("file")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return {"message": "Files uploaded successfully", "file_path": file_path}, 200
    else:
        return jsonify({"message": "file format is invalid"}), 400


# route for processing pdf
# POST /process
@app.route('/process', methods=['GET'])
def process():
    file_path = request.args.get("file_path")
    if not file_path or not os.path.exists(file_path):
        return jsonify({"message": "file path is invalid"}), 400

    PROJECT_ID = os.environ.get("PROJECT_ID")
    LOCATION = os.environ.get("LOCATION")
    PROCESSOR_ID = os.environ.get("PROCESSOR_ID")
    try:
        extracted_text = process_pdf(PROJECT_ID, LOCATION, PROCESSOR_ID, file_path)
        summary = summarize_text(extracted_text)
        return jsonify({"text": extracted_text, "summary": summary}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "PDF processing failed"}), 500



if __name__ == '__main__':
    app.run(debug=True)
