from django.views     import View
from django.http      import JsonResponse
from django.db.models import Prefetch

from .models        import (
    HashTag,
    Photo
)
from account.models import (
    User,
    Collection
)
from auth           import login_check

class RelatedPhotoView(View):
    PHOTO_LIMIT = 20

    def get(self, request, photo_id):
        try:
            if Photo.objects.filter(id=photo_id).exists():
                related_tags = list(HashTag.objects.filter(photo__id = photo_id).values_list('name', flat=True))
                photos = Photo.objects.filter(hashtag__name__in = related_tags).exclude(id=photo_id).prefetch_related("user").distinct()
                result = [{
                    "id"                 : photo.id,
                    "image"              : photo.image,
                    "location"           : photo.location,
                    "user_first_name"    : photo.user.first_name,
                    "user_last_name"     : photo.user.last_name,
                    "user_name"          : photo.user.user_name,
                    "user_profile_image" : photo.user.profile_image
                } for photo in photos[:self.PHOTO_LIMIT]]

                return JsonResponse({"tags" : related_tags, "data" : result}, status=200)
            return JsonResponse({"message" : "NON_EXISTING_PHOTO"}, status=401)
        except ValueError:
            return JsonResponse({"message" : "INVALID_PHOTO"}, status=400)

class RelatedCollectionView(View):
    LIMIT_NUM = 3

    def get(self, request, photo_id):
        try:
            if Photo.objects.filter(id=photo_id).exists():
                collections = Collection.objects.filter(
                    photocollection__photo__id = photo_id
                ).exclude(user=User.objects.get(user_name='weplash')).prefetch_related(
                    Prefetch("photo_set"),
                    Prefetch("photo_set__hashtag")
                )

                result = [{
                    "id"              : collection.id,
                    "image"           : [photo.image for photo in collection.photo_set.all()[:self.LIMIT_NUM]],
                    "name"            : collection.name,
                    "photos_number"   : collection.photo_set.all().count(),
                    "user_first_name" : collection.user.first_name,
                    "user_last_name"  : collection.user.last_name,
                    'tags'            : [tag.name for tag in collection.photo_set.filter().first().hashtag.all()[:self.LIMIT_NUM]]
                } for collection in collections]

                return JsonResponse({'data' : result}, status=200)
            return JsonResponse({"message" : "NON_EXISTING_PHOTO"}, status=401)
        except ValueError:
            return JsonResponse({"message" : "INVALID_PHOTO"}, status=400)

class SearchBarView(View):
    def get(self, request):
        result = list(HashTag.objects.all().order_by('name').values_list('name', flat=True))
        return JsonResponse({"data" : result}, status=200)

class UserCardView(View):
    PHOTO_LIMIT = 3

    @login_check
    def get(self, request, user_id, user_name):
        try:
            user = User.objects.prefetch_related("photo_set", "following").get(user_name=user_name)

            result = {
                "id"                    : user.id,
                "user_first_name"       : user.first_name,
                "user_last_name"        : user.last_name,
                "user_name"             : user.user_name,
                "user_profile_image"    : user.profile_image,
                "photos"                : [photo.image for photo in user.photo_set.all()[:self.PHOTO_LIMIT]],
            }

            if user.id != user_id:
                result['follow'] = user.follower.filter(from_user_id=user_id, status=True).exists()
            else:
                result['follow'] = 'self'

            return JsonResponse({'data' : result}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message' : 'NON_EXISTING_USER'}, status=401)
