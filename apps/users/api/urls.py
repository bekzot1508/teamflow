from django.urls import path

from .views import UserMeAPIView, UserRegisterAPIView

urlpatterns = [
    path("me/", UserMeAPIView.as_view(), name="user-me"),
    path("register/", UserRegisterAPIView.as_view(), name="user-register"),
]