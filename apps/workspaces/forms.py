from django import forms

from .models import Workspace, WorkspaceMember
from django.contrib.auth import get_user_model

User = get_user_model()


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


#_____________ WorkSpace Member Add _____________
class WorkspaceMemberAddForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
            "placeholder": "user@example.com",
        })
    )

    role = forms.ChoiceField(
        choices=[
            (WorkspaceMember.Role.ADMIN, "Admin"),
            (WorkspaceMember.Role.MEMBER, "Member"),
            (WorkspaceMember.Role.VIEWER, "Viewer"),
        ],
        widget=forms.Select(attrs={
            "class": "w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500",
        })
    )


#_____________ WorkSpace Member Role Update _____________
class WorkspaceMemberRoleUpdateForm(forms.Form):
    role = forms.ChoiceField(
        choices=[
            (WorkspaceMember.Role.ADMIN, "Admin"),
            (WorkspaceMember.Role.MEMBER, "Member"),
            (WorkspaceMember.Role.VIEWER, "Viewer"),
        ],
        widget=forms.Select(attrs={
            "class": "border rounded-lg px-3 py-2 text-sm",
        })
    )