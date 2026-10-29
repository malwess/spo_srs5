// ===== Список заданий: фильтры через fetch(), вид таблица/карточки, обновление строк =====
(function () {
    const rows = document.getElementById('task-rows');
    if (!rows) return;
    const { state, api } = Planner;
    const filters = document.getElementById('task-filters');    // есть только на странице «Задания»
    const tiles = document.getElementById('task-tiles');
    const view = document.getElementById('tasks-view');

    // ---------- Страница дисциплины: только точечное обновление строк ----------
    if (!filters) {
        const rowById = id => rows.querySelector('tr[data-id="' + id + '"]');
        const insert = html => {
            rows.querySelector('.js-empty')?.remove();
            rows.insertAdjacentHTML('afterbegin', html);
        };
        document.addEventListener('planner:status', e => {
            const old = rowById(e.detail.id);
            if (old) old.outerHTML = e.detail.row;
        });
        document.addEventListener('planner:created', e => {
            if (String(e.detail.subject) === rows.dataset.subject) insert(e.detail.row);
        });
        document.addEventListener('planner:deleted', e => rowById(e.detail.id)?.remove());
        return;
    }

    // ---------- Страница «Задания»: фильтры и поиск ----------
    const loading = document.getElementById('tasks-loading');
    const found = document.getElementById('found-count');
    let timer = null;
    let lastRequest = 0;

    function readFilters() {
        return {
            q: filters.elements.q.value.trim(),
            subject: filters.elements.subject.value,
            status: filters.elements.status.value,
        };
    }

    function writeFilters(values) {
        filters.elements.q.value = values.q || '';
        filters.elements.subject.value = values.subject || '';
        filters.elements.status.value = values.status || '';
    }

    async function loadTasks() {
        const values = readFilters();
        state.set('tasks.filters', values);                      // запоминаем фильтры
        const request = ++lastRequest;
        loading.classList.add('show');
        const data = await api('/api/tasks/?' + new URLSearchParams(values));
        if (request !== lastRequest) return;                    // пришёл ответ на устаревший запрос
        rows.innerHTML = data.rows;
        tiles.innerHTML = data.tiles;
        found.textContent = data.count;
        Planner.initTooltips(view);
        loading.classList.remove('show');
    }

    filters.addEventListener('change', loadTasks);
    filters.addEventListener('submit', e => e.preventDefault());
    filters.elements.q.addEventListener('input', () => {        // поиск с задержкой 300 мс
        clearTimeout(timer);
        timer = setTimeout(loadTasks, 300);
    });

    document.getElementById('reset-filters').addEventListener('click', () => {
        writeFilters({});
        loadTasks();
    });

    // После изменения данных перерисовываем список с текущими фильтрами
    ['planner:status', 'planner:created', 'planner:deleted'].forEach(name =>
        document.addEventListener(name, loadTasks));

    // ---------- Вид списка: таблица или карточки (сохраняется: tasks.view) ----------
    const switcher = document.getElementById('view-switch');

    function setView(mode) {
        view.dataset.view = mode;
        switcher.querySelectorAll('[data-view]').forEach(btn =>
            btn.classList.toggle('active', btn.dataset.view === mode));
    }

    switcher.addEventListener('click', event => {
        const btn = event.target.closest('[data-view]');
        if (!btn) return;
        state.set('tasks.view', btn.dataset.view);
        setView(btn.dataset.view);
    });

    // ---------- Восстановление состояния ----------
    setView(state.get('tasks.view', 'table'));
    const saved = state.get('tasks.filters', null);
    if (saved && (saved.q || saved.subject || saved.status)) {
        writeFilters(saved);
        loadTasks();
    }
})();
