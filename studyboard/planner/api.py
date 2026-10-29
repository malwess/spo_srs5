"""JSON API для действий без перезагрузки страницы (вызываются через fetch)."""
import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST

from .forms import TaskForm
from .models import ChecklistItem, Task
from .services import filter_tasks, task_stats


def read_json(request):
    try:
        return json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return {}


def task_payload(request, task):
    """Данные задания и готовые HTML-фрагменты для вставки на страницу."""
    return {
        'id': task.pk,
        'subject': task.subject_id,
        'status': task.status,
        'status_label': task.get_status_display(),
        'card': render_to_string('partials/_task_card.html', {'task': task}, request),
        'row': render_to_string('partials/_task_row.html', {'task': task}, request),
        'tile': render_to_string('partials/_task_tile.html', {'task': task}, request),
    }


@require_GET
def tasks(request):
    """GET /api/tasks/?subject=&status=&q= — отфильтрованный список заданий."""
    found = filter_tasks(request.GET)
    return JsonResponse({
        'count': found.count(),
        'rows': render_to_string('partials/_task_rows.html', {'tasks': found}, request),
        'tiles': render_to_string('partials/_task_tiles.html', {'tasks': found}, request),
    })


@require_POST
def task_create(request):
    """POST /api/tasks/create/ — добавление задания из модального окна."""
    form = TaskForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    task = form.save()
    return JsonResponse({'ok': True, 'task': task_payload(request, task), 'stats': task_stats()})


@require_POST
def task_status(request, pk):
    """POST /api/tasks/<id>/status/ — смена статуса (доска, список, главная)."""
    task = get_object_or_404(Task, pk=pk)
    status = read_json(request).get('status')
    if status not in dict(Task.STATUSES):
        return JsonResponse({'ok': False, 'error': 'Неизвестный статус'}, status=400)
    task.status = status
    task.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'ok': True, 'task': task_payload(request, task), 'stats': task_stats()})


@require_POST
def task_delete(request, pk):
    """POST /api/tasks/<id>/delete/ — удаление задания."""
    task = get_object_or_404(Task, pk=pk)
    title = str(task)
    task.delete()
    return JsonResponse({'ok': True, 'title': title, 'stats': task_stats()})


@require_POST
def checklist_add(request, pk):
    """POST /api/tasks/<id>/checklist/ — новый пункт чек-листа."""
    task = get_object_or_404(Task, pk=pk)
    text = (read_json(request).get('text') or '').strip()
    if not text:
        return JsonResponse({'ok': False, 'error': 'Введите текст пункта'}, status=400)
    item = ChecklistItem.objects.create(task=task, text=text[:200], order=task.checklist.count())
    return JsonResponse({
        'ok': True,
        'html': render_to_string('partials/_checklist_item.html', {'item': item}, request),
        'progress': task.checklist_progress(),
    })


@require_POST
def checklist_toggle(request, pk):
    """POST /api/checklist/<id>/toggle/ — отметить пункт выполненным или снять отметку."""
    item = get_object_or_404(ChecklistItem, pk=pk)
    item.done = not item.done
    item.save(update_fields=['done'])
    return JsonResponse({'ok': True, 'done': item.done, 'progress': item.task.checklist_progress()})
