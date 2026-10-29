from django.urls import path

from . import api, views

urlpatterns = [
    # страницы
    path('', views.dashboard, name='dashboard'),
    path('board/', views.board, name='board'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),

    # JSON API для fetch()
    path('api/tasks/', api.tasks, name='api_tasks'),
    path('api/tasks/create/', api.task_create, name='api_task_create'),
    path('api/tasks/<int:pk>/status/', api.task_status, name='api_task_status'),
    path('api/tasks/<int:pk>/delete/', api.task_delete, name='api_task_delete'),
    path('api/tasks/<int:pk>/checklist/', api.checklist_add, name='api_checklist_add'),
    path('api/checklist/<int:pk>/toggle/', api.checklist_toggle, name='api_checklist_toggle'),
]
