// ===== Канбан-доска: перетаскивание, фильтр, свёрнутая колонка, вкладки на телефоне =====
(function () {
    const board = document.getElementById('board');
    if (!board) return;
    const { state } = Planner;

    const column = status => board.querySelector('.board-column[data-status="' + status + '"] .board-column-body');
    const cardById = id => board.querySelector('.task-card[data-id="' + id + '"]');

    function toElement(html) {
        const box = document.createElement('div');
        box.innerHTML = html.trim();
        return box.firstElementChild;
    }

    // Счётчики в заголовках колонок и во вкладках (учитывают фильтр)
    function updateCounts() {
        board.querySelectorAll('.board-column').forEach(col => {
            const visible = col.querySelectorAll('.task-card:not(.d-none)').length;
            document.querySelectorAll('[data-count="' + col.dataset.status + '"]')
                .forEach(el => { el.textContent = visible; });
        });
    }

    // --- Фильтр по дисциплине (сохраняется: board.subject) ---
    const filter = document.getElementById('board-filter');

    function applyFilter(subject) {
        filter.querySelectorAll('[data-subject]').forEach(btn =>
            btn.classList.toggle('active', btn.dataset.subject === subject));
        board.querySelectorAll('.task-card').forEach(card =>
            card.classList.toggle('d-none', subject !== '' && card.dataset.subject !== subject));
        updateCounts();
    }

    filter.addEventListener('click', event => {
        const btn = event.target.closest('[data-subject]');
        if (!btn) return;
        state.set('board.subject', btn.dataset.subject);
        applyFilter(btn.dataset.subject);
    });

    // --- Перетаскивание карточек между колонками (HTML5 Drag and Drop) ---
    board.addEventListener('dragstart', event => {
        const card = event.target.closest('.task-card');
        if (!card) return;
        event.dataTransfer.setData('text/plain', card.dataset.id);
        event.dataTransfer.effectAllowed = 'move';
        card.classList.add('dragging');
    });
    board.addEventListener('dragend', event => {
        const card = event.target.closest('.task-card');
        if (card) card.classList.remove('dragging');
        board.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    });
    board.querySelectorAll('[data-dropzone]').forEach(zone => {
        zone.addEventListener('dragover', event => {
            event.preventDefault();
            zone.classList.add('drag-over');
        });
        zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
        zone.addEventListener('drop', async event => {
            event.preventDefault();
            zone.classList.remove('drag-over');
            const id = event.dataTransfer.getData('text/plain');
            const card = cardById(id);
            if (!card || card.dataset.status === zone.dataset.dropzone) return;
            zone.prepend(card);                                   // сразу показываем результат
            try {
                await Planner.setStatus(id, zone.dataset.dropzone);  // и сохраняем на сервере
            } catch (e) {
                column(card.dataset.status).prepend(card);           // при ошибке возвращаем назад
            }
        });
    });

    // --- Реакция на события других компонентов ---
    document.addEventListener('planner:status', event => {
        const task = event.detail;
        const old = cardById(task.id);
        const card = toElement(task.card);
        card.classList.toggle('d-none', old ? old.classList.contains('d-none') : false);
        if (old) old.remove();
        column(task.status).prepend(card);
        card.classList.add('flash');
        updateCounts();
    });

    document.addEventListener('planner:created', event => {
        const card = toElement(event.detail.card);
        const subject = state.get('board.subject', '');
        card.classList.toggle('d-none', subject !== '' && card.dataset.subject !== subject);
        column(event.detail.status).prepend(card);
        card.classList.add('flash');
        updateCounts();
    });

    document.addEventListener('planner:deleted', event => {
        const card = cardById(event.detail.id);
        if (card) card.remove();
        updateCounts();
    });

    // --- Сворачивание колонки «Сдано» (сохраняется: board.doneCollapsed) ---
    const doneColumn = board.querySelector('.board-column[data-status="done"]');
    const toggleDone = document.getElementById('toggle-done');

    function setDoneCollapsed(collapsed) {
        doneColumn.classList.toggle('collapsed', collapsed);
        toggleDone.querySelector('i').className = collapsed ? 'ti ti-chevrons-down' : 'ti ti-chevrons-up';
        board.classList.toggle('done-collapsed', collapsed);
    }

    toggleDone.addEventListener('click', () => {
        const collapsed = !doneColumn.classList.contains('collapsed');
        state.set('board.doneCollapsed', collapsed);
        setDoneCollapsed(collapsed);
    });

    // --- Вкладки колонок на телефоне (сохраняется: board.tab) ---
    const tabs = document.getElementById('board-tabs');

    function showTab(status) {
        tabs.querySelectorAll('[data-tab]').forEach(t => t.classList.toggle('active', t.dataset.tab === status));
        board.querySelectorAll('.board-column').forEach(c => c.classList.toggle('is-active', c.dataset.status === status));
    }

    tabs.addEventListener('click', event => {
        const tab = event.target.closest('[data-tab]');
        if (!tab) return;
        state.set('board.tab', tab.dataset.tab);
        showTab(tab.dataset.tab);
    });

    // --- Восстановление сохранённого состояния при загрузке страницы ---
    applyFilter(state.get('board.subject', ''));
    setDoneCollapsed(state.get('board.doneCollapsed', false));
    showTab(state.get('board.tab', 'todo'));
})();
