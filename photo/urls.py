from django.urls import path

from .views import (
    UploadView,
    RelatedPhotoView,
    RelatedCollectionView,
    PhotoView,
    SearchBarView,
    UserCardView,
    LikePhotoView,
    BackgroundView
)

urlpatterns= [
    path('/user-card/<user_name>', UserCardView.as_view()),
    path('/related-photo/<photo_id>', RelatedPhotoView.as_view()),
    path('/related-collection/<photo_id>', RelatedCollectionView.as_view()),
    path('',PhotoView.as_view()),
    path('/back/<collection_name>',BackgroundView.as_view()),
    path('/upload', UploadView.as_view()),
    path('/search', SearchBarView.as_view()),
    path('/like', LikePhotoView.as_view())
]
