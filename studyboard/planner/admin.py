from django.contrib import admin

from .models import ChecklistItem, Subject, Task

admin.site.site_header = 'Учебный планировщик'
admin.site.site_title = 'Учебный планировщик'
admin.site.index_title = 'Управление данными'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name', 'teacher', 'control', 'color')
    search_fields = ('name', 'short_name', 'teacher')


class ChecklistInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'subject', 'deadline', 'status', 'priority')
    list_filter = ('subject', 'status', 'kind')
    search_fields = ('title', 'description')
    inlines = [ChecklistInline]
