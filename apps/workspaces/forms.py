from django import forms

from .models import Workspace

#_____________ WorkSpace Create _____________
class WorkspaceCreateForm(forms.ModelForm):
    class Meta:
        model = Workspace
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
                "placeholder": "Example: Utopia Team",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
                "rows": 4,
                "placeholder": "Short description about this workspace",
            }),
        }