from django.urls import path

from .views import (
    ProfileView,
)

urlpatterns = [
    path('/@<user_name>', ProfileView.as_view()),
]
