// ===== Модальное окно «Новое задание»: отправка формы через fetch() =====
(function () {
    const form = document.getElementById('task-form');
    if (!form) return;
    const modalEl = document.getElementById('task-modal');
    const submit = form.querySelector('[type=submit]');
    const spinner = submit.querySelector('.spinner-border');

    function clearErrors() {
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        form.querySelectorAll('[data-error-for]').forEach(el => { el.textContent = ''; });
    }

    function showErrors(errors) {
        Object.entries(errors).forEach(([name, messages]) => {
            const field = form.elements[name];
            const box = form.querySelector('[data-error-for="' + name + '"]');
            if (field) field.classList.add('is-invalid');
            if (box) box.textContent = messages.join(' ');
        });
    }

    form.addEventListener('submit', async (event) => {
        event.preventDefault();               // страница не перезагружается
        clearErrors();
        submit.disabled = true;
        spinner.classList.remove('d-none');
        try {
            const data = await Planner.api(form.action, { method: 'POST', form });
            if (!data.ok) {
                showErrors(data.errors);
                return;
            }
            Planner.updateCounters(data.stats);
            Planner.toast('Задание «' + form.elements.title.value + '» добавлено');
            const keepSubject = form.elements.subject.value;
            form.reset();
            form.elements.subject.value = keepSubject;
            tabler.bootstrap.Modal.getOrCreateInstance(modalEl).hide();
            // Сообщаем странице (доске или списку), что появилось новое задание
            document.dispatchEvent(new CustomEvent('planner:created', { detail: data.task }));
        } finally {
            submit.disabled = false;
            spinner.classList.add('d-none');
        }
    });

    modalEl.addEventListener('hidden.bs.modal', clearErrors);
})();
