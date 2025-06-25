from flask import Flask, render_template, request
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
    return render_template('index.html', langs=LANG_OPTIONS, original_text=None, translated_text=None)

@app.route('/transcrever', methods=['POST'])
def transcrever():
    file = request.files['audio']
    src_lang = request.form['src_lang']
    tgt_lang = request.form['tgt_lang']
    user_name = request.form.get('user_name')
    subject = request.form.get('subject')
    save_db = request.form.get('save') == '1'

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    original_text = transcribe_audio(file_path, LANG_CODE[src_lang])
    translated_text = translate_text(original_text, LANG_CODE[src_lang], LANG_CODE[tgt_lang])

    if save_db and user_name and subject:
        save_record(user_name, subject, file_path, original_text, translated_text)

    return render_template('index.html', langs=LANG_OPTIONS, original_text=original_text, translated_text=translated_text)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
