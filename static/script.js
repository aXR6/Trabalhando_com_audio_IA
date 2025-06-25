
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('audio-form');
    const progress = document.getElementById('progress');
    const originalText = document.getElementById('original_text');
    const translatedText = document.getElementById('translated_text');

    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        progress.innerHTML = '<div class="d-flex align-items-center"><div class="spinner-border me-2" role="status"></div><strong>Extraindo texto...</strong></div>';
        originalText.textContent = '';
        translatedText.textContent = '';

        const formData = new FormData(form);

        try {
            const resp = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });
            if (!resp.ok) throw new Error();
            const data = await resp.json();
            originalText.textContent = data.original_text;

            progress.innerHTML = '<div class="d-flex align-items-center"><div class="spinner-border me-2" role="status"></div><strong>Traduzindo...</strong></div>';

            const translateData = new FormData();
            translateData.append('text', data.original_text);
            translateData.append('src_lang', formData.get('src_lang'));
            translateData.append('tgt_lang', formData.get('tgt_lang'));
            translateData.append('user_name', formData.get('user_name'));
            translateData.append('subject', formData.get('subject'));
            translateData.append('save', formData.get('save'));
            translateData.append('file_path', data.file_path);

            const resp2 = await fetch('/api/translate', {
                method: 'POST',
                body: translateData
            });
            if (!resp2.ok) throw new Error();
            const data2 = await resp2.json();
            translatedText.textContent = data2.translated_text;
            progress.innerHTML = '';
        } catch (err) {
            progress.innerHTML = '<span class="text-danger">Ocorreu um erro no processamento.</span>';
        }
    });
});

