from datetime import date

from django.db.models import Case, IntegerField, When

from .models import Task


def task_stats():
    """Счётчики заданий для меню, главной страницы и ответов API."""
    tasks = Task.objects.all()
    return {
        'total': tasks.count(),
        'todo': tasks.filter(status=Task.TODO).count(),
        'doing': tasks.filter(status=Task.DOING).count(),
        'done': tasks.filter(status=Task.DONE).count(),
        'overdue': tasks.exclude(status=Task.DONE).filter(deadline__lt=date.today()).count(),
    }


def filter_tasks(params):
    """Отбор заданий по дисциплине, статусу и строке поиска."""
    tasks = Task.objects.select_related('subject').prefetch_related('checklist')
    subject = params.get('subject')
    status = params.get('status')
    query = (params.get('q') or '').strip()

    if subject:
        tasks = tasks.filter(subject_id=subject)
    if status == 'overdue':
        tasks = tasks.exclude(status=Task.DONE).filter(deadline__lt=date.today())
    elif status:
        tasks = tasks.filter(status=status)
    if query:
        # SQLite не умеет сравнивать русские буквы без учёта регистра,
        # поэтому поиск выполняется в Python через casefold()
        query = query.casefold()
        ids = [t.pk for t in tasks
               if query in f'{t.code} {t.title} {t.description} {t.subject.short_name}'.casefold()]
        tasks = tasks.filter(pk__in=ids)

    # Сначала несданные задания по сроку, сданные — в конце списка
    is_done = Case(When(status=Task.DONE, then=1), default=0, output_field=IntegerField())
    return tasks.order_by(is_done, 'deadline')
