from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from speech import transcribe_audio
from translation import translate_text
from languages import LANG_CODE
from db import init_db, save_record

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

LANG_OPTIONS = list(LANG_CODE.keys())

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', langs=LANG_OPTIONS, results=None)

@app.route('/transcrever', methods=['POST'])
def transcrever():
    files = request.files.getlist('audio')
    src_lang = request.form['src_lang']
    tgt_lang = request.form['tgt_lang']
    user_name = request.form.get('user_name')
    session_name = request.form.get('session_name')
    subject = request.form.get('subject')
    save_db = request.form.get('save') == '1'

    results = []
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        original_text = transcribe_audio(file_path, LANG_CODE[src_lang])
        translated_text = translate_text(original_text, LANG_CODE[src_lang], LANG_CODE[tgt_lang])

        if save_db and user_name and session_name and subject:
            save_record(user_name, session_name, subject, file_path, original_text, translated_text)

        results.append({'filename': filename, 'original_text': original_text, 'translated_text': translated_text})

    return render_template('index.html', langs=LANG_OPTIONS, results=results)

@app.route('/api/transcribe', methods=['POST'])
def api_transcribe():
    file = request.files['audio']
    src_lang = request.form['src_lang']

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    original_text = transcribe_audio(file_path, LANG_CODE[src_lang])
    return jsonify({'original_text': original_text, 'file_path': file_path})


@app.route('/api/translate', methods=['POST'])
def api_translate():
    text = request.form['text']
    src_lang = request.form['src_lang']
    tgt_lang = request.form['tgt_lang']
    file_path = request.form.get('file_path')
    user_name = request.form.get('user_name')
    session_name = request.form.get('session_name')
    subject = request.form.get('subject')
    save_db = request.form.get('save') == '1'

    translated_text = translate_text(text, LANG_CODE[src_lang], LANG_CODE[tgt_lang])

    if save_db and user_name and session_name and subject and file_path:
        save_record(user_name, session_name, subject, file_path, text, translated_text)

    return jsonify({'translated_text': translated_text})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
