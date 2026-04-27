from django import forms

from .models import Project


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "placeholder": "Project name",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "rows": 3,
            }),
        }