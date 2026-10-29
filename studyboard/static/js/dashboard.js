// ===== Главная страница: диаграмма статусов и отметка «Сдано» в списке сроков =====
(function () {
    const data = JSON.parse(document.getElementById('chart-data').textContent);  // данные из БД
    const dark = document.documentElement.getAttribute('data-bs-theme') === 'dark';

    const chart = new ApexCharts(document.getElementById('status-chart'), {
        chart: { type: 'donut', height: 260, fontFamily: 'inherit', background: 'transparent' },
        theme: { mode: dark ? 'dark' : 'light' },
        series: data.values,
        labels: data.labels,
        colors: ['#066fd1', '#f76707', '#2fb344'],
        legend: { position: 'bottom' },
        dataLabels: { enabled: true },
        plotOptions: { pie: { donut: { size: '62%', labels: { show: true,
            total: { show: true, label: 'Всего', formatter: w => w.globals.seriesTotals.reduce((a, b) => a + b, 0) } } } } },
        responsive: [{ breakpoint: 576, options: { chart: { height: 230 } } }],
    });
    chart.render();

    // Когда статус изменился, диаграмма перерисовывается по новым счётчикам
    document.addEventListener('planner:stats', event => {
        const s = event.detail;
        chart.updateSeries([s.todo, s.doing, s.done]);
    });

    // Сданное задание плавно убирается из списка ближайших сроков
    document.addEventListener('planner:status', event => {
        if (event.detail.status !== 'done') return;
        const item = document.querySelector('.upcoming-item[data-id="' + event.detail.id + '"]');
        if (!item) return;
        item.classList.add('removing');
        setTimeout(() => item.remove(), 400);
    });
})();
