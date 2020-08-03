from django.urls import (
    path,
    include
)

urlpatterns = [
    path('photo', include('photo.urls')),
    path('account', include('account.urls'))
]
