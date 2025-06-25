
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('audio-form');
    const progress = document.getElementById('progress');
    const progressBar = document.getElementById('progress-bar');
    const progressLabel = document.getElementById('progress-label');
    const resultsBox = document.getElementById('results');

    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        resultsBox.innerHTML = '';
        progressBar.style.width = '0%';
        progressLabel.textContent = '';

        const files = document.getElementById('audio').files;
        const commonData = new FormData(form);

        try {
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                progressLabel.innerHTML = '<div class="d-flex align-items-center"><div class="spinner-border me-2" role="status"></div><strong>Processando ' + file.name + '...</strong></div>';
                progressBar.style.width = ((i / files.length) * 100) + '%';

                const fd = new FormData();
                fd.append('audio', file);
                fd.append('src_lang', commonData.get('src_lang'));

                const resp = await fetch('/api/transcribe', { method: 'POST', body: fd });
                if (!resp.ok) { progressLabel.textContent = 'Erro na transcrição'; break; }
                const data = await resp.json();

                progressLabel.innerHTML = '<div class="d-flex align-items-center"><div class="spinner-border me-2" role="status"></div><strong>Traduzindo...</strong></div>';

                const td = new FormData();
                td.append('text', data.original_text);
                td.append('src_lang', commonData.get('src_lang'));
                td.append('tgt_lang', commonData.get('tgt_lang'));
                td.append('user_name', commonData.get('user_name'));
                td.append('session_name', commonData.get('session_name'));
                td.append('subject', commonData.get('subject'));
                td.append('save', commonData.get('save'));
                td.append('file_path', data.file_path);

                const resp2 = await fetch('/api/translate', { method: 'POST', body: td });
                if (!resp2.ok) { progressLabel.textContent = 'Erro na tradução'; break; }
                const data2 = await resp2.json();

                const item = document.createElement('div');
                item.className = 'mb-4';
                item.innerHTML = '<h4>' + file.name + '</h4>' +
                    '<strong>Texto Extraído:</strong><p>' + data.original_text + '</p>' +
                    '<strong>Texto Traduzido:</strong><p>' + data2.translated_text + '</p>';
                resultsBox.appendChild(item);
                progressBar.style.width = (((i + 1) / files.length) * 100) + '%';
            }
            progressLabel.innerHTML = '<span class="text-success">Concluído.</span>';
        } catch (err) {
            progressLabel.innerHTML = '<span class="text-danger">Ocorreu um erro no processamento.</span>';
        }
    });
});

