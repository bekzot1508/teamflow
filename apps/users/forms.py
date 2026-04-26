from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "username", "full_name"]

    def clean(self):
        cleaned = super().clean()

        if cleaned.get("password1") != cleaned.get("password2"):
            raise forms.ValidationError("Passwords do not match")

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user