from django import forms

from .models import Project


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "rows": 3,
            }),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if len(name) < 3:
            raise forms.ValidationError("Project name must be at least 3 characters.")

        return name


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full border rounded-lg px-3 py-2",
                "rows": 3,
            }),
        }