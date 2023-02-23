from django.urls import path
from .views import RegisterationAPIView
from .views import LoginAPIView

app_name = "Authentication"
urlpatterns = [
    path('users/register', RegisterationAPIView.as_view()),
    path('users/login', LoginAPIView.as_view())
]