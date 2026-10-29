from datetime import date

from django.db import models


class Subject(models.Model):
    """Учебная дисциплина."""

    COLORS = [
        ('blue', 'Синий'),
        ('green', 'Зелёный'),
        ('orange', 'Оранжевый'),
        ('purple', 'Фиолетовый'),
        ('red', 'Красный'),
        ('teal', 'Бирюзовый'),
    ]
    CONTROLS = [
        ('exam', 'Экзамен'),
        ('credit', 'Зачёт'),
        ('diff', 'Дифф. зачёт'),
    ]

    name = models.CharField('Название', max_length=150)
    short_name = models.CharField('Сокращение', max_length=20)
    teacher = models.CharField('Преподаватель', max_length=100, blank=True)
    control = models.CharField('Форма контроля', max_length=10, choices=CONTROLS, default='exam')
    color = models.CharField('Цвет', max_length=10, choices=COLORS, default='blue')

    class Meta:
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'
        ordering = ['name']

    def __str__(self):
        return self.short_name

    def progress(self):
        """Процент сданных заданий по дисциплине."""
        total = self.tasks.count()
        if total == 0:
            return 0
        return round(self.tasks.filter(status=Task.DONE).count() * 100 / total)


class Task(models.Model):
    """Учебное задание: ПЗ, СРС, ЛР или домашнее задание."""

    TODO, DOING, DONE = 'todo', 'doing', 'done'
    STATUSES = [
        (TODO, 'К выполнению'),
        (DOING, 'В работе'),
        (DONE, 'Сдано'),
    ]
    KINDS = [
        ('pz', 'ПЗ'),
        ('srs', 'СРС'),
        ('lr', 'ЛР'),
        ('dz', 'ДЗ'),
    ]
    PRIORITIES = [
        (1, 'Низкий'),
        (2, 'Обычный'),
        (3, 'Высокий'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='tasks',
                                verbose_name='Дисциплина')
    kind = models.CharField('Вид работы', max_length=5, choices=KINDS, default='pz')
    number = models.PositiveSmallIntegerField('Номер', default=1)
    title = models.CharField('Тема', max_length=200)
    description = models.TextField('Описание', blank=True)
    deadline = models.DateField('Срок сдачи')
    status = models.CharField('Статус', max_length=10, choices=STATUSES, default=TODO)
    priority = models.PositiveSmallIntegerField('Приоритет', choices=PRIORITIES, default=2)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['deadline', '-priority']

    def __str__(self):
        return f'{self.code} {self.title}'

    @property
    def code(self):
        """Короткое обозначение, например «СРС 5»."""
        return f'{self.get_kind_display()} {self.number}'

    @property
    def days_left(self):
        return (self.deadline - date.today()).days

    @property
    def is_overdue(self):
        return self.status != self.DONE and self.days_left < 0

    def checklist_progress(self):
        items = list(self.checklist.all())
        if not items:
            return 0
        return round(sum(i.done for i in items) * 100 / len(items))


class ChecklistItem(models.Model):
    """Пункт чек-листа задания (подзадача)."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='checklist',
                             verbose_name='Задание')
    text = models.CharField('Пункт', max_length=200)
    done = models.BooleanField('Выполнено', default=False)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Пункт чек-листа'
        verbose_name_plural = 'Пункты чек-листа'
        ordering = ['order', 'id']

    def __str__(self):
        return self.text
