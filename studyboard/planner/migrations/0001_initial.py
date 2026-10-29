import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Subject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=150, verbose_name="Название")),
                (
                    "short_name",
                    models.CharField(max_length=20, verbose_name="Сокращение"),
                ),
                (
                    "teacher",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Преподаватель"
                    ),
                ),
                (
                    "control",
                    models.CharField(
                        choices=[
                            ("exam", "Экзамен"),
                            ("credit", "Зачёт"),
                            ("diff", "Дифф. зачёт"),
                        ],
                        default="exam",
                        max_length=10,
                        verbose_name="Форма контроля",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        choices=[
                            ("blue", "Синий"),
                            ("green", "Зелёный"),
                            ("orange", "Оранжевый"),
                            ("purple", "Фиолетовый"),
                            ("red", "Красный"),
                            ("teal", "Бирюзовый"),
                        ],
                        default="blue",
                        max_length=10,
                        verbose_name="Цвет",
                    ),
                ),
            ],
            options={
                "verbose_name": "Дисциплина",
                "verbose_name_plural": "Дисциплины",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("pz", "ПЗ"),
                            ("srs", "СРС"),
                            ("lr", "ЛР"),
                            ("dz", "ДЗ"),
                        ],
                        default="pz",
                        max_length=5,
                        verbose_name="Вид работы",
                    ),
                ),
                (
                    "number",
                    models.PositiveSmallIntegerField(default=1, verbose_name="Номер"),
                ),
                ("title", models.CharField(max_length=200, verbose_name="Тема")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("deadline", models.DateField(verbose_name="Срок сдачи")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("todo", "К выполнению"),
                            ("doing", "В работе"),
                            ("done", "Сдано"),
                        ],
                        default="todo",
                        max_length=10,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Низкий"), (2, "Обычный"), (3, "Высокий")],
                        default=2,
                        verbose_name="Приоритет",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создано"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Изменено"),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="planner.subject",
                        verbose_name="Дисциплина",
                    ),
                ),
            ],
            options={
                "verbose_name": "Задание",
                "verbose_name_plural": "Задания",
                "ordering": ["deadline", "-priority"],
            },
        ),
        migrations.CreateModel(
            name="ChecklistItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=200, verbose_name="Пункт")),
                ("done", models.BooleanField(default=False, verbose_name="Выполнено")),
                (
                    "order",
                    models.PositiveSmallIntegerField(default=0, verbose_name="Порядок"),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checklist",
                        to="planner.task",
                        verbose_name="Задание",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пункт чек-листа",
                "verbose_name_plural": "Пункты чек-листа",
                "ordering": ["order", "id"],
            },
        ),
    ]
