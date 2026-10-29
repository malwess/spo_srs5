from django import template

register = template.Library()

STATUS_COLORS = {'todo': 'blue', 'doing': 'orange', 'done': 'green'}
STATUS_ICONS = {'todo': 'ti-circle-dashed', 'doing': 'ti-progress', 'done': 'ti-circle-check'}


def plural_ru(n, one, few, many):
    """Русское склонение: 1 день, 2 дня, 5 дней."""
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


@register.filter
def days_word(n):
    return f'{abs(n)} {plural_ru(n, "день", "дня", "дней")}'


@register.filter
def deadline_text(task):
    """Подпись срока: «сегодня», «через 3 дня», «просрочено на 2 дня»."""
    if task.status == 'done':
        return 'сдано'
    days = task.days_left
    if days == 0:
        return 'сегодня'
    if days == 1:
        return 'завтра'
    if days > 0:
        return f'через {days_word(days)}'
    return f'просрочено на {days_word(days)}'


@register.filter
def deadline_color(task):
    """Цвет метки срока по количеству оставшихся дней."""
    if task.status == 'done':
        return 'green'
    days = task.days_left
    if days < 0:
        return 'red'
    if days <= 3:
        return 'orange'
    return 'secondary'


@register.filter
def status_color(status):
    return STATUS_COLORS.get(status, 'secondary')


@register.filter
def status_icon(status):
    return STATUS_ICONS.get(status, 'ti-circle')


@register.inclusion_tag('partials/_progress.html')
def progress_bar(value, color='primary', size='sm'):
    """Полоса прогресса Tabler: {% progress_bar 75 'green' %}."""
    return {'value': value, 'color': color, 'size': size}
