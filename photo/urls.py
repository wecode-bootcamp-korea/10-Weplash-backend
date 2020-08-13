from django.urls import path

from .views import (
    UploadView,
    RelatedPhotoView,
    RelatedCollectionView,
    PhotoView,
    SearchBarView,
    UserCardView,
    LikePhotoView,
    BackgroundView,
    CollectionMainView,
    RelatedPhotoBackColorView,
    ModalCollectionView,
    AddCollectionView,
    CreateCollectionView
)

urlpatterns= [
    path('/user-card/<user_name>', UserCardView.as_view()),
    path('/related-photo/<photo_id>', RelatedPhotoView.as_view()),
    path('/related-collection', RelatedCollectionView.as_view()),
    path('',PhotoView.as_view()),
    path('/back/<collection_name>',BackgroundView.as_view()),
    path('/main-collection', CollectionMainView.as_view()),
    path('/upload', UploadView.as_view()),
    path('/search', SearchBarView.as_view()),
    path('/like', LikePhotoView.as_view()),
    path('/back/related-photo/<photo_id>', RelatedPhotoBackColorView.as_view()),
    path('/add', AddCollectionView.as_view()),
    path('/create', CreateCollectionView.as_view()),
    path('/<int:photo_id>', ModalCollectionView.as_view())
]
