from django.shortcuts import render


#____________ Dashboard ____________
def dashboard(request):
    return render(request, "dashboard.html")