from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    """Форма быстрого добавления задания (используется в модальном окне)."""

    class Meta:
        model = Task
        fields = ['subject', 'kind', 'number', 'title', 'deadline', 'priority', 'description']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'kind': forms.Select(attrs={'class': 'form-select'}),
            'number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Например: Модели Django и ORM'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'},
                                        format='%Y-%m-%d'),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                 'placeholder': 'Что нужно сделать и сдать'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].empty_label = 'Выберите дисциплину'
