// ===== Общий модуль приложения: запросы к API, состояние, уведомления =====
window.Planner = (function () {

    // --- 1. Состояние интерфейса в localStorage ---
    const state = {
        get(key, fallback) {
            try {
                const raw = localStorage.getItem('planner.' + key);
                return raw === null ? fallback : JSON.parse(raw);
            } catch (e) {
                return fallback;
            }
        },
        set(key, value) {
            try {
                localStorage.setItem('planner.' + key, JSON.stringify(value));
            } catch (e) { /* хранилище недоступно — работаем без сохранения */ }
        },
    };

    // --- 2. Запрос к API через fetch() с CSRF-токеном Django ---
    function csrfToken() {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    async function api(url, options = {}) {
        const settings = {
            method: options.method || 'GET',
            headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'fetch' },
        };
        if (options.json !== undefined) {
            settings.headers['Content-Type'] = 'application/json';
            settings.body = JSON.stringify(options.json);
        } else if (options.form) {
            settings.body = new FormData(options.form);
        }
        const response = await fetch(url, settings);
        const data = await response.json().catch(() => ({}));
        if (!response.ok && !data.errors) {
            toast(data.error || 'Ошибка сервера: ' + response.status, 'danger');
            throw new Error(data.error || response.statusText);
        }
        return data;
    }

    // --- 3. Всплывающие уведомления (компонент Toast из Tabler) ---
    function toast(text, color = 'success') {
        const icons = { success: 'ti-circle-check', danger: 'ti-alert-circle', info: 'ti-info-circle' };
        const el = document.createElement('div');
        el.className = 'toast align-items-center border-0 text-bg-' + color;
        el.setAttribute('role', 'status');
        el.innerHTML = '<div class="d-flex"><div class="toast-body"><i class="ti ' + (icons[color] || icons.info) +
            ' me-2"></i>' + text + '</div><button type="button" class="btn-close btn-close-white me-2 m-auto" ' +
            'data-bs-dismiss="toast" aria-label="Закрыть"></button></div>';
        document.getElementById('toasts').appendChild(el);
        const t = new tabler.bootstrap.Toast(el, { delay: 3000 });
        el.addEventListener('hidden.bs.toast', () => el.remove());
        t.show();
    }

    // --- 4. Обновление счётчиков на всей странице после изменения данных ---
    function updateCounters(stats) {
        if (!stats) return;
        document.querySelectorAll('[data-counter]').forEach(el => {
            const value = stats[el.dataset.counter];
            if (value === undefined) return;
            el.textContent = value;
            if (el.classList.contains('nav-badge')) el.hidden = value === 0;
        });
        document.dispatchEvent(new CustomEvent('planner:stats', { detail: stats }));
    }

    // --- 5. Смена статуса задания (используется доской, списком и главной) ---
    async function setStatus(id, status) {
        const data = await api('/api/tasks/' + id + '/status/', { method: 'POST', json: { status } });
        updateCounters(data.stats);
        toast('«' + data.task.status_label + '»: статус задания обновлён');
        document.dispatchEvent(new CustomEvent('planner:status', { detail: data.task }));
        return data.task;
    }

    // --- 6. Удаление задания в два нажатия (без системного окна confirm) ---
    async function deleteTask(button) {
        if (!button.classList.contains('confirm')) {
            button.classList.add('confirm');
            button.lastChild.textContent = 'Нажмите ещё раз';
            setTimeout(() => button.classList.remove('confirm'), 4000);
            return null;
        }
        const id = button.dataset.id;
        const data = await api('/api/tasks/' + id + '/delete/', { method: 'POST' });
        updateCounters(data.stats);
        toast('Задание «' + data.title + '» удалено', 'info');
        document.dispatchEvent(new CustomEvent('planner:deleted', { detail: { id } }));
        return id;
    }

    // --- Общие обработчики, работающие на всех страницах ---
    function initTooltips(root = document) {
        root.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            tabler.bootstrap.Tooltip.getOrCreateInstance(el);
        });
    }

    function initTheme() {
        document.querySelectorAll('.js-theme-toggle').forEach(btn => {
            btn.addEventListener('click', () => {
                const dark = document.documentElement.getAttribute('data-bs-theme') !== 'dark';
                if (dark) document.documentElement.setAttribute('data-bs-theme', 'dark');
                else document.documentElement.removeAttribute('data-bs-theme');
                state.set('theme', dark ? 'dark' : 'light');
            });
        });
    }

    function initSidebarFold() {
        const btn = document.getElementById('sidebar-fold');
        if (!btn) return;
        btn.addEventListener('click', () => {
            const html = document.documentElement;
            const folded = html.getAttribute('data-bs-sidebar') !== 'folded';
            if (folded) html.setAttribute('data-bs-sidebar', 'folded');
            else html.removeAttribute('data-bs-sidebar');
            state.set('sidebarFolded', folded);
        });
    }

    function initToday() {
        const label = document.getElementById('today-label');
        if (label) {
            label.textContent = new Date().toLocaleDateString('ru-RU',
                { weekday: 'long', day: 'numeric', month: 'long' });
        }
    }

    // Делегирование событий: кнопки появляются и после вставки HTML из fetch
    document.addEventListener('click', async (event) => {
        const statusBtn = event.target.closest('.js-set-status');
        if (statusBtn && !statusBtn.closest('#task-detail')) {
            event.preventDefault();
            await setStatus(statusBtn.dataset.id, statusBtn.dataset.status);
        }
        const deleteBtn = event.target.closest('.js-delete');
        if (deleteBtn) {
            event.preventDefault();
            event.stopPropagation();
            await deleteTask(deleteBtn);
        }
    });

    document.addEventListener('change', async (event) => {
        const box = event.target.closest('.js-done-toggle');
        if (box) {
            box.disabled = true;
            try {
                await setStatus(box.dataset.id, box.checked ? 'done' : 'doing');
            } catch (e) {
                box.checked = !box.checked;
            }
            box.disabled = false;
        }
    });

    document.addEventListener('DOMContentLoaded', () => {
        initTooltips();
        initTheme();
        initSidebarFold();
        initToday();
    });

    return { state, api, toast, updateCounters, setStatus, initTooltips };
})();
