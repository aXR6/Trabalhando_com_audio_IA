from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from speech import transcribe_audio
from translation import translate_text
from languages import LANG_CODE
from db import init_db, save_record, list_sessions, list_records

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

LANG_OPTIONS = list(LANG_CODE.keys())

@app.route('/', methods=['GET', 'POST'])
def sessions_view():
    """Prompt for user name and show existing sessions."""
    user_name = None
    sessions = None
    if request.method == 'POST':
        user_name = request.form['user_name']
        sessions = list_sessions(user_name)
    elif request.args.get('user_name'):
        user_name = request.args['user_name']
        sessions = list_sessions(user_name)
    return render_template('sessions.html', user_name=user_name, sessions=sessions)


@app.route('/panel', methods=['GET'])
def index():
    user_name = request.args.get('user_name')
    session_name = request.args.get('session_name')
    if not user_name or not session_name:
        return redirect(url_for('sessions_view'))
    records = list_records(user_name, session_name)
    return render_template(
        'index.html',
        langs=LANG_OPTIONS,
        results=None,
        records=records,
        user_name=user_name,
        session_name=session_name,
    )

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

    records = list_records(user_name, session_name)
    return render_template(
        'index.html',
        langs=LANG_OPTIONS,
        results=results,
        records=records,
        user_name=user_name,
        session_name=session_name,
    )

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
