from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(filename)
    return {'message': 'file uploaded'}


if __name__ == '__main__':
    app.run(debug=True)
