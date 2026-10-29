// ===== Страница задания: смена статуса и чек-лист без перезагрузки =====
(function () {
    const page = document.getElementById('task-detail');
    if (!page) return;
    const { api } = Planner;
    const percent = document.getElementById('checklist-percent');
    const bar = document.getElementById('checklist-bar');
    const list = document.getElementById('checklist');
    const form = document.getElementById('checklist-form');

    function showProgress(value) {
        percent.textContent = value + '%';
        bar.style.width = value + '%';
    }

    // Переключатель статуса: подсвечиваем выбранную кнопку цветом статуса
    page.querySelectorAll('.status-switch .js-set-status').forEach(btn => {
        btn.addEventListener('click', async () => {
            const task = await Planner.setStatus(btn.dataset.id, btn.dataset.status);
            page.querySelectorAll('.status-switch .js-set-status').forEach(b => {
                const active = b.dataset.status === task.status;
                b.classList.toggle('active', active);
                b.classList.toggle('btn-' + b.dataset.color, active);
            });
        });
    });

    // Отметка пункта чек-листа
    list.addEventListener('change', async event => {
        const box = event.target.closest('.js-check');
        if (!box) return;
        const data = await api('/api/checklist/' + box.dataset.id + '/toggle/', { method: 'POST' });
        box.closest('.checklist-item').classList.toggle('is-done', data.done);
        showProgress(data.progress);
    });

    // Добавление пункта чек-листа
    form.addEventListener('submit', async event => {
        event.preventDefault();
        const input = form.elements.text;
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            return;
        }
        input.classList.remove('is-invalid');
        const data = await api(form.dataset.url, { method: 'POST', json: { text: input.value } });
        list.insertAdjacentHTML('beforeend', data.html);
        showProgress(data.progress);
        input.value = '';
        Planner.toast('Пункт добавлен в чек-лист');
    });
})();
