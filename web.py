from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash,
)
from werkzeug.utils import secure_filename
import os
from speech import transcribe_audio
from translation import translate_text
from languages import LANG_CODE
from db import (
    init_db,
    save_record,
    list_sessions,
    list_records,
    ensure_session,
    ensure_user,
    create_user,
    verify_user,
    reset_password,
    get_user_id,
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "devkey")
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

LANG_OPTIONS = list(LANG_CODE.keys())

@app.route('/', methods=['GET', 'POST'])
def login_view():
    """Login using user name and password."""
    if session.get('user_name'):
        return redirect(url_for('sessions_view'))
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        if verify_user(user_name, password):
            session['user_name'] = user_name
            return redirect(url_for('sessions_view'))
        flash('Credenciais inválidas')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        pin = request.form['pin']
        if get_user_id(user_name):
            flash('Usuário já existe')
        else:
            create_user(user_name, password, pin)
            flash('Usuário criado com sucesso')
            return redirect(url_for('login_view'))
    return render_template('register.html')


@app.route('/reset', methods=['GET', 'POST'])
def reset_view():
    if request.method == 'POST':
        user_name = request.form['user_name']
        pin = request.form['pin']
        new_password = request.form['new_password']
        if reset_password(user_name, pin, new_password):
            flash('Senha atualizada')
            return redirect(url_for('login_view'))
        flash('PIN inválido')
    return render_template('reset.html')


@app.route('/logout')
def logout_view():
    session.clear()
    return redirect(url_for('login_view'))


@app.route('/sessions', methods=['GET'])
def sessions_view():
    """Show sessions for the logged in user."""
    user_name = session.get('user_name')
    if not user_name:
        return redirect(url_for('login_view'))
    sessions = list_sessions(user_name)
    return render_template('sessions.html', user_name=user_name, sessions=sessions)


@app.route('/panel', methods=['GET'])
def index():
    user_name = session.get('user_name')
    session_name = request.args.get('session_name')
    if not user_name or not session_name:
        return redirect(url_for('sessions_view'))
    ensure_session(user_name, session_name)
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
    user_name = session.get('user_name')
    session_name = request.form.get('session_name')
    if not user_name or not session_name:
        return redirect(url_for('sessions_view'))
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
    user_name = session.get('user_name')
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
