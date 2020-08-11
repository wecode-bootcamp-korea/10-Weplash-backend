from django.urls import path

from .views import (
    RelatedPhotoView,
    RelatedCollectionView,
    SearchBarView
)

urlpatterns= [
    path('/related-photo/<photo_id>', RelatedPhotoView.as_view()),
    path('/related-collection/<photo_id>', RelatedCollectionView.as_view()),
    path('/search', SearchBarView.as_view())
    ]
