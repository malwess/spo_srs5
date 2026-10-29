from datetime import date

from django.core.management.base import BaseCommand

from planner.models import ChecklistItem, Subject, Task

REPORT_STEPS = ['Написать код', 'Сделать скриншоты страниц', 'Оформить отчёт в Word', 'Сдать преподавателю']
COLAB_STEPS = ['Выполнить расчёты в Google Colab', 'Построить графики', 'Оформить отчёт', 'Отправить ссылку на Colab']

SUBJECTS = [
    ('Структура программного обеспечения и базы данных', 'СПОиБД', 'Манин А. Н.', 'exam', 'blue'),
    ('Специальные главы высшей математики', 'СВМ', '', 'exam', 'purple'),
    ('Прикладные методы обработки и защиты данных', 'ПМОиЗД', '', 'credit', 'orange'),
    ('Информатика', 'Инф', '', 'diff', 'green'),
]

# (дисциплина, вид, номер, тема, срок, статус, приоритет, описание, шаги чек-листа, сколько шагов выполнено)
TASKS = [
    ('СПОиБД', 'pz', 1, 'Веб-приложение на Flask', date(2026, 9, 25), 'done', 2,
     'Создать простое веб-приложение на Flask по методическим указаниям к ПЗ 1.', REPORT_STEPS, 4),
    ('СПОиБД', 'pz', 3, 'Установка Django. Пользователи и авторизация', date(2026, 10, 9), 'done', 2,
     'Проект django_auth: вход и выход, страница профиля, суперпользователь.', REPORT_STEPS, 4),
    ('СПОиБД', 'srs', 3, 'Группы пользователей и разграничение прав доступа', date(2026, 10, 16), 'done', 2,
     'Группы Django, проверка прав в шаблонах и представлениях, Bootstrap.', REPORT_STEPS, 4),
    ('СПОиБД', 'pz', 4, 'Модели Django, ORM, миграции и административная панель', date(2026, 10, 20), 'done', 2,
     'Модели факультетов, курсов и профилей студентов, регистрация в админке.', REPORT_STEPS, 4),
    ('СПОиБД', 'srs', 4, 'Связанные модели и ограничение доступа', date(2026, 10, 23), 'done', 3,
     'Учебные группы, роль «Методист», формы и CRUD-страницы.', REPORT_STEPS, 4),
    ('СПОиБД', 'pz', 5, 'Применение шаблона Tabler к сайту', date(2026, 10, 30), 'done', 2,
     'Перевести интерфейс сайта django_auth на Tabler, проверить адаптивность.', REPORT_STEPS, 4),
    ('СПОиБД', 'srs', 5, 'Интерактивный frontend-интерфейс на Django и Tabler', date(2026, 11, 6), 'doing', 3,
     'Новый проект: не менее 4 компонентов, 3 страниц, 3 действий через fetch(), '
     'сохранение состояния и адаптивность.', REPORT_STEPS, 1),
    ('СВМ', 'lr', 1, 'Лабораторная работа 1 (вариант 3)', date(2026, 10, 10), 'todo', 3,
     'Долг: выполнить и сдать лабораторную работу по своему варианту.', COLAB_STEPS, 0),
    ('СВМ', 'pz', 2, 'Методы уточнения корней нелинейных уравнений в Excel', date(2026, 10, 14), 'done', 2,
     'Бисекция, хорды, Ньютон и простая итерация в Microsoft Excel.', ['Построить график функции',
     'Локализовать корень', 'Заполнить таблицы методов', 'Сводная таблица сравнения'], 4),
    ('СВМ', 'srs', 2, 'Программная реализация численных методов решения нелинейных уравнений',
     date(2026, 10, 21), 'doing', 3,
     'Вариант 10, вместе с Юндой М. В. Python, NumPy и SciPy в Google Colab, сравнение с Excel.',
     ['Табулирование и локализация корня', 'Бисекция и хорды', 'Ньютон и простая итерация',
      'Сравнение со SciPy и Excel', 'Отправить ссылку на Colab'], 2),
    ('ПМОиЗД', 'dz', 1, 'Первичный анализ данных о материалах в Google Colab', date(2026, 10, 2), 'done', 2,
     'Набор Materials Project Data, выполнение ячеек и материаловедческие выводы.', COLAB_STEPS, 4),
    ('ПМОиЗД', 'pz', 3, 'Формирование аналитического набора данных', date(2026, 10, 16), 'done', 2,
     'Объединение семи CSV-файлов в pandas, очистка ключей, новые признаки.', COLAB_STEPS, 4),
    ('ПМОиЗД', 'lr', 3, 'Лабораторная работа 3 (вариант 3)', date(2026, 10, 30), 'todo', 2,
     'Ноутбук Colab и отчёт в Word по своему варианту.', COLAB_STEPS, 0),
    ('Инф', 'lr', 1, 'Лабораторная работа (вариант 3)', date(2026, 10, 12), 'done', 1,
     'Лабораторная работа по информатике по варианту 3.', ['Решить задачи варианта', 'Оформить отчёт'], 2),
]


class Command(BaseCommand):
    help = 'Заполняет базу дисциплинами и заданиями студентки'

    def handle(self, *args, **options):
        ChecklistItem.objects.all().delete()
        Task.objects.all().delete()
        Subject.objects.all().delete()

        subjects = {}
        for name, short, teacher, control, color in SUBJECTS:
            subjects[short] = Subject.objects.create(name=name, short_name=short, teacher=teacher,
                                                     control=control, color=color)

        for short, kind, number, title, deadline, status, prio, descr, steps, done in TASKS:
            task = Task.objects.create(subject=subjects[short], kind=kind, number=number, title=title,
                                       deadline=deadline, status=status, priority=prio, description=descr)
            for i, text in enumerate(steps):
                ChecklistItem.objects.create(task=task, text=text, done=i < done, order=i)

        self.stdout.write(self.style.SUCCESS(
            f'Создано дисциплин: {Subject.objects.count()}, заданий: {Task.objects.count()}, '
            f'пунктов чек-листа: {ChecklistItem.objects.count()}'))
