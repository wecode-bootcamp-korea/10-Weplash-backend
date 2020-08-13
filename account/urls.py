from django.urls import path

from .views import (
    SignUpView,
    SignInView,
    KakaoSignInView,
    ProfileView,
    FollowingView
)

urlpatterns = [
    path('/sign-up', SignUpView.as_view()),
    path('/sign-in', SignInView.as_view()),
    path('/kakao', KakaoSignInView.as_view()),
    path('', ProfileView.as_view()),
    path('/following', FollowingView.as_view())
]
