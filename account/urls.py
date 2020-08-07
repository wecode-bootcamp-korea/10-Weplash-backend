from django.urls import path

from .views import (
    SignUpView,
    SignInView
    ProfileView
)

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view())
    path('/@<user_name>', ProfileView.as_view())
]
