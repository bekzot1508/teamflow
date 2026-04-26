from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.views import View

from .forms import RegisterForm
from .services import register_user


#____________ Register ____________
class RegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = register_user(
                email=form.cleaned_data["email"],
                username=form.cleaned_data["username"],
                full_name=form.cleaned_data["full_name"],
                password=form.cleaned_data["password1"],
            )

            login(request, user)
            messages.success(request, "Account created successfully")

            return redirect("dashboard")

        return render(request, self.template_name, {"form": form})


#____________ Login ____________
class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        user = authenticate(
            request,
            email=request.POST.get("email"),
            password=request.POST.get("password"),
        )

        if user:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid credentials")
        return redirect("login")


#____________ Logout ____________
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")