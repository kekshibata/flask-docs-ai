import base64
import os

import openai
import tiktoken
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import documentai, firestore, storage
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = "uploads"

ALLOWED_EXTENSIONS = set(["pdf"])

# Initialize Firestore DB
db = firestore.Client(project=os.environ.get("PROJECT_ID"))
storage_client = storage.Client()
bucket_name = "for-docs-ai"
bucket = storage_client.get_bucket(bucket_name)


# ファイルの拡張子をチェックする
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# テキストのトークン数を数える
def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    return len(tokens)


# リストを指定したサイズで分割する
def split_list_by_size(lst, size):
    result = []
    for i in range(0, len(lst), size):
        result.append(lst[i:i+size])
    return result


# テキストをトークン数で分割する
def split_text_by_tokens(text, max_tokens):
    chunks = []
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoding.encode(text)
    split_tokens = split_list_by_size(tokens, max_tokens)
    for tokens in split_tokens:
        chunks.append(encoding.decode(tokens))
    return chunks


# chunkを指定した文字数で要約する
def summarize_chunk(chunk, char_count=300):
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful asistant"},
                {"role": "user", "content": f"summarize this text in Japanese, within {char_count} characters: {chunk}"},
                ]
            )
    return response.choices[0]['message']['content']


# テキストを指定した文字数で要約する
def summarize_text(text, char_count=300):
    max_tokens = 4000
    token_count = count_tokens(text)
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    if token_count <= max_tokens:
        return summarize_chunk(text, char_count)

    chunks = split_text_by_tokens(text, max_tokens)
    summaries = []
    for chunk in chunks:
        summaries.append(summarize_chunk(chunk))

    text = "".join(summaries)
    print(text)
    return summarize_chunk(text, char_count)


# pdfファイルをDocument AIで処理する
def process_pdf(project_id, location, processor_id, file):
    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(project_id, location, processor_id)
    raw_document = documentai.RawDocument(content=file, mime_type="application/pdf")
    request_ = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request_)

    return result.document.text


# PDFをアップロードする
@app.route('/upload', methods=['POST'])
def upload_file():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if 'file' not in request.files:
        return jsonify({"message": "ファイルがありません"}), 400

    file = request.files.get('file')
    char_count = int(request.form["charCount"])

    if file and allowed_file(file.filename):
        # GCSにファイルをアップロードする
        filename = secure_filename(file.filename)
        blob = bucket.blob(filename)
        blob.upload_from_string(file.read(), content_type=file.content_type)

        # Firestoreにファイルのメタデータと抽出されたテキストを保存する
        doc_ref = db.collection('files').document()
        doc_ref.set({
            'filename': filename,
            'content_type': file.content_type,
            'uploaded_at': firestore.SERVER_TIMESTAMP
        })

        return {"message": "Files uploaded successfully", "file_id": doc_ref.id, "char_Count": char_count}, 200
    else:
        return jsonify({"message": "file format is invalid"}), 400


# PDFを処理する
@app.route('/process', methods=['GET'])
def process():
    file_id = request.args.get("file_id")
    char_count = request.args.get("charCount")

    if not file_id:
        return jsonify({"message": "invalid file ID"}), 400

    doc_ref = db.collection('files').document(file_id)
    filename = doc_ref.get().to_dict()['filename']

    PROJECT_ID = os.environ.get("PROJECT_ID")
    LOCATION = os.environ.get("LOCATION")
    PROCESSOR_ID = os.environ.get("PROCESSOR_ID")
    try:
        blob = bucket.blob(filename)
        if not blob:
            return jsonify({"message": "file not found"}), 404
        file = blob.download_as_bytes()
    except Exception as e:
        print(e)
        return jsonify({"message": str(e)}), 500

    extracted_text = process_pdf(PROJECT_ID, LOCATION, PROCESSOR_ID, file)
    summary = summarize_text(extracted_text, char_count)

    doc_ref.update({
        'extracted_text': extracted_text,
        'summary': summary
    })

    return jsonify({"text": extracted_text, "summary": summary}), 200


if __name__ == '__main__':
    app.run(debug=True)
