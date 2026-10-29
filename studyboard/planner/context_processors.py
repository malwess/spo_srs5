from .services import task_stats


def counters(request):
    """Счётчики заданий для бейджей в боковом меню (доступны во всех шаблонах)."""
    return {'counters': task_stats()}
