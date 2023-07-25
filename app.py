from flask import Flask, request, render_template, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from markupsafe import Markup
import os

import book_analysis

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = os.urandom(12).hex()


@app.route('/')
def index():
    message = request.args.get('message')
    if message:
        message = Markup(message)
    return render_template('index.html', message=message)


@app.route('/upload', methods=['POST'])
def upload_file():
    f = request.files['file']
    if f and f.filename.endswith('.pdf'):
        for filename in os.listdir('current_book'):
            filepath = os.path.join('current_book', filename)
            os.remove(filepath)
        filename = secure_filename(f.filename)
        f.save(os.path.join('current_book', filename))
        session['uploaded_file'] = filename
        return jsonify({'message': f'File <b>{filename}</b> uploaded successfully!'})

    return 'Something went wrong!'


@app.route('/current_book/<filename>')
def uploaded_file(filename):
    return send_from_directory('current_book', filename)


@app.route('/uploaded_file')
def get_uploaded_file():
    return session.get('uploaded_file', '')


@app.route('/pdf_container')
def pdf_container():
    return render_template('pdf_container.html')


@app.route('/pdf-grid')
def pdf_grid():
    directory_path = 'current_book'
    file_name = os.listdir(directory_path)[0]
    sims = book_analysis.analyze_book(os.path.join(directory_path, file_name))
    sims_sorted = sorted(sims, key=lambda x: x[1], reverse=True)
    res = sims_sorted[:12]

    directory_path = app.config['BOOKS_DIRECTORY']
    file_names = sorted(os.listdir(directory_path))

    top = [(item[0], item[1], file_names[item[0]]) for item in res]
    return render_template('pdf-grid.html', top=top)


@app.route('/send_file/<path:filename>')
def send_file(filename):
    return send_from_directory(app.config['BOOKS_DIRECTORY'], filename)


if __name__ == '__main__':
    app.run()
