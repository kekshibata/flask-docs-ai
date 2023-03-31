import io
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import documentai
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"


def process_pdf(project_id, location, processor_id, file_path):
    client = documentai.DocumentProcessorServiceClient()

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processors/processor-id
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
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    files = request.files.getlist("files")
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        if file.filename.lower().endswith(".pdf"):
            # Replace with your project ID, location, and processor ID
            project_id = os.environ.get("PROJECT_ID")
            location = os.environ.get("LOCATION")
            processor_id = os.environ.get("PROCESSOR_ID")
            text = process_pdf(project_id, location, processor_id, file_path)
            return jsonify({"message": "PDF processed", "content": text}), 200

    return {"message": "Files uploaded successfully"}, 200


if __name__ == '__main__':
    app.run(debug=True)
