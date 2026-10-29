from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import TaskForm
from .models import Subject, Task
from .services import filter_tasks, task_stats


@ensure_csrf_cookie
def dashboard(request):
    """Главная: статистика, прогресс по дисциплинам и ближайшие сроки."""
    stats = task_stats()
    upcoming = (Task.objects.select_related('subject')
                .exclude(status=Task.DONE).order_by('deadline')[:6])
    chart = {
        'labels': ['К выполнению', 'В работе', 'Сдано'],
        'values': [stats['todo'], stats['doing'], stats['done']],
    }
    return render(request, 'planner/dashboard.html', {
        'stats': stats,
        'subjects': Subject.objects.prefetch_related('tasks'),
        'upcoming': upcoming,
        'chart': chart,
    })


@ensure_csrf_cookie
def board(request):
    """Канбан-доска: три колонки по статусам."""
    tasks = Task.objects.select_related('subject').prefetch_related('checklist')
    columns = [
        {'status': code, 'title': title, 'tasks': [t for t in tasks if t.status == code]}
        for code, title in Task.STATUSES
    ]
    return render(request, 'planner/board.html', {
        'columns': columns,
        'subjects': Subject.objects.all(),
        'form': TaskForm(),
    })


@ensure_csrf_cookie
def task_list(request):
    """Список заданий с фильтрами (сами фильтры работают через fetch)."""
    return render(request, 'planner/task_list.html', {
        'tasks': filter_tasks({}),
        'subjects': Subject.objects.all(),
        'statuses': Task.STATUSES,
        'form': TaskForm(),
    })


@ensure_csrf_cookie
def task_detail(request, pk):
    task = get_object_or_404(Task.objects.select_related('subject'), pk=pk)
    return render(request, 'planner/task_detail.html', {
        'task': task,
        'statuses': Task.STATUSES,
    })


@ensure_csrf_cookie
def subject_list(request):
    return render(request, 'planner/subject_list.html', {
        'subjects': Subject.objects.prefetch_related('tasks'),
    })


@ensure_csrf_cookie
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'planner/subject_detail.html', {
        'subject': subject,
        'tasks': filter_tasks({'subject': subject.pk}),
        'form': TaskForm(initial={'subject': subject}),
    })
