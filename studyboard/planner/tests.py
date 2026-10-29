import json
from datetime import date, timedelta

from django.test import TestCase

from .models import ChecklistItem, Subject, Task


class PlannerApiTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name='Базы данных', short_name='БД')
        self.task = Task.objects.create(subject=self.subject, title='Модели Django',
                                        deadline=date.today() + timedelta(days=3))
        self.item = ChecklistItem.objects.create(task=self.task, text='Написать код')

    def post_json(self, url, data=None):
        return self.client.post(url, json.dumps(data or {}), content_type='application/json')

    def test_pages_open(self):
        for url in ['/', '/board/', '/tasks/', f'/tasks/{self.task.pk}/', '/subjects/',
                    f'/subjects/{self.subject.pk}/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_filter_and_search(self):
        data = self.client.get('/api/tasks/', {'q': 'МОДЕЛИ'}).json()     # поиск без учёта регистра
        self.assertEqual(data['count'], 1)
        data = self.client.get('/api/tasks/', {'status': 'done'}).json()
        self.assertEqual(data['count'], 0)

    def test_create_task(self):
        response = self.client.post('/api/tasks/create/', {
            'subject': self.subject.pk, 'kind': 'srs', 'number': 5, 'title': 'Интерфейс на Tabler',
            'deadline': '2026-11-06', 'priority': 3, 'description': ''})
        self.assertTrue(response.json()['ok'])
        self.assertEqual(Task.objects.count(), 2)

    def test_create_task_errors(self):
        response = self.client.post('/api/tasks/create/', {'title': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('subject', response.json()['errors'])

    def test_change_status(self):
        data = self.post_json(f'/api/tasks/{self.task.pk}/status/', {'status': 'done'}).json()
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')
        self.assertEqual(data['stats']['done'], 1)
        self.assertEqual(self.post_json(f'/api/tasks/{self.task.pk}/status/', {'status': 'x'}).status_code, 400)

    def test_checklist(self):
        data = self.post_json(f'/api/checklist/{self.item.pk}/toggle/').json()
        self.assertTrue(data['done'])
        self.assertEqual(data['progress'], 100)
        data = self.post_json(f'/api/tasks/{self.task.pk}/checklist/', {'text': 'Сделать отчёт'}).json()
        self.assertEqual(data['progress'], 50)

    def test_delete_task(self):
        self.post_json(f'/api/tasks/{self.task.pk}/delete/')
        self.assertFalse(Task.objects.exists())

    def test_get_not_allowed_for_actions(self):
        self.assertEqual(self.client.get(f'/api/tasks/{self.task.pk}/delete/').status_code, 405)
