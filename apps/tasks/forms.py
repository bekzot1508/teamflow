from django import forms
from django.utils import timezone

from .models import Task


#____________ Task Create ____________#
class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "priority",
            "assignee",
            "deadline",
        )
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "placeholder": "Task title",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "rows": 4,
            }),
            "priority": forms.Select(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
            }),
            "assignee": forms.Select(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
            }),
            "deadline": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "w-full border rounded-lg px-3 py-2",
            }),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")

        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past.")

        return deadline


#____________ Task Update ____________#
class TaskUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "title",
            "description",
            "priority",
            "assignee",
            "deadline",
        )
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "rows": 4,
            }),
            "priority": forms.Select(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
            }),
            "assignee": forms.Select(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
            }),
            "deadline": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "w-full border rounded-lg px-3 py-2",
            }),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")

        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past.")

        return deadline


#____________ Task Comment ____________#
class TaskCommentForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "w-full border rounded-lg px-3 py-2",
            "rows": 3,
            "placeholder": "Write a comment... use @username to mention",
        })
    )


#_____________ Task Attachment ____________#
class TaskAttachmentForm(forms.Form):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            "class": "w-full border rounded-lg px-3 py-2",
        })
    )


class TaskMoveForm(forms.Form):
    column_id = forms.IntegerField()
    target_position = forms.IntegerField(required=False, min_value=0)