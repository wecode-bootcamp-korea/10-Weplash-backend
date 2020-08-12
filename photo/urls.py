from django.urls import path

from .views import (
    RelatedPhotoView,
    RelatedCollectionView,
    SearchBarView,
    UserCardView
)

urlpatterns= [
    path('/user-card/<user_name>', UserCardView.as_view()),
    path('/related-photo/<photo_id>', RelatedPhotoView.as_view()),
    path('/related-collection/<photo_id>', RelatedCollectionView.as_view()),
    path('/search', SearchBarView.as_view())
]
