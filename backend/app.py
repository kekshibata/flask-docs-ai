import io
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import documentai
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"


def process_pdf(project_id, location, processor_id, file):
    client = documentai.DocumentProcessorServiceClient()

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processors/processor-id
    name = client.processor_path(project_id, location, processor_id)

    with io.BytesIO() as buf:
        buf.write(file.read())
        # input_config = {
        #     "gcs_source": {
        #         "uri": f"gs://{gcs_bucket}/{gcs_file_path}"
        #     },
        #     "mime_type": "application/pdf"
        # }
        # Read the file into memory
        buf.seek(0)
        raw_document = documentai.RawDocument(content=buf.read(), mime_type="application/pdf")

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
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        if file.filename.lower().endswith(".pdf"):
            # Replace with your project ID, location, and processor ID
            project_id = os.environ.get("PROJECT_ID")
            location = os.environ.get("LOCATION")
            processor_id = os.environ.get("PROCESSOR_ID")
            text = process_pdf(project_id, location, processor_id, file)
            return jsonify({"message": "PDF processed", "content": text}), 200

    return {"message": "Files uploaded successfully"}, 200


if __name__ == '__main__':
    app.run(debug=True)
