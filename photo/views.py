import uuid
import json
import boto3
from PIL            import Image
from urllib.request import urlopen

from django.core.cache import cache
from django.db         import transaction
from django.views      import View
from django.db.models  import (
    Prefetch,
    Q,
    F,
    Count
)

from django.http import (
    JsonResponse,
    HttpResponse
)

from auth    import login_check
from .models import (
    HashTag,
    Photo,
    PhotoCollection,
    BackGroundColor,
    PhotoHashTag
)

from account.models import (
    User,
    Collection,
    Like,
    Follow
)

from photo.tasks import upload_image
from my_settings import AWS_S3

class RelatedPhotoView(View):
    PHOTO_LIMIT = 20
    @login_check
    def get(self, request, user_id, photo_id):
        try:
            photo       = Photo.objects.get(id=photo_id)
            photo.views = F('views') +1
            photo.save()
            related_tags = list(HashTag.objects.filter(photo__id = photo_id).values_list('name', flat=True))

            photos = Photo.objects.filter(
                hashtag__name__in = related_tags
            ).exclude(id=photo_id).prefetch_related("user").distinct()

            likes = set(Like.objects.filter(
                user_id   = user_id,
                status    = True,
                photo__in = list(photos)
            ).values_list('photo_id', flat=True))

            collections = set(PhotoCollection.objects.filter(
                collection__user_id = user_id,
                photo__in           = list(photos)
            ).values_list('photo_id', flat=True))

            result = [{
                "id"                 : photo.id,
                "image"              : photo.image,
                "location"           : photo.location,
                "user_first_name"    : photo.user.first_name,
                "user_last_name"     : photo.user.last_name,
                "user_name"          : photo.user.user_name,
                "user_profile_image" : photo.user.profile_image,
                "user_like"          : True if photo.id in likes else False,
                "user_collection"    : True if photo.id in collections else False
            } for photo in photos[:self.PHOTO_LIMIT]]
            return JsonResponse({"tags":related_tags, "data":result}, status=200)
        except Photo.DoesNotExist:
            return JsonResponse({'message':'NON_EXISTING_PHOTO'}, status=401)
        except ValueError:
            return JsonResponse({"message":"INVALID_PHOTO"}, status=400)

class RelatedCollectionView(View):
    LIMIT_NUM = 3
    def get(self, request):
        try:
            photo_id  = request.GET.get('photo', None)
            user_name = request.GET.get('user', None)
            query = Q()

            if photo_id:
                if Photo.objects.filter(id=photo_id).exists():
                    query &= Q(photocollection__photo__id=int(photo_id))
                else:
                    return JsonResponse({'message':"NON_EXISTING_PHOTO"}, status=401)
            elif user_name:
                if User.objects.filter(user_name=user_name).exists():
                    query &= Q(user__user_name=user_name)
                else:
                    return JsonResponse({'message':"NON_EXISTING_USER"}, status=401)

            collections = Collection.objects.filter(query).exclude(
                user__user_name = 'weplash'
            ).prefetch_related(Prefetch("photo_set"), Prefetch("photo_set__hashtag"))

            if photo_id:
                collections = collections[:self.LIMIT_NUM]

            result = [{
                "id"              : collection.id,
                "image"           : [photo.image for photo in collection.photo_set.all()[:self.LIMIT_NUM]],
                "name"            : collection.name,
                "photos_number"   : collection.photo_set.all().count(),
                "user_first_name" : collection.user.first_name,
                "user_last_name"  : collection.user.last_name,
                "tags"            : [tag.name for tag in collection.photo_set.first().hashtag.all()[:self.LIMIT_NUM]]
            } for collection in collections]
            return JsonResponse({'data':result}, status=200)
        except ValueError:
            return JsonResponse({"message":"INVALID_KEY"}, status=400)

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
                "id"                 : user.id,
                "user_first_name"    : user.first_name,
                "user_last_name"     : user.last_name,
                "user_name"          : user.user_name,
                "user_profile_image" : user.profile_image,
                "photos"             : [photo.image for photo in user.photo_set.all()[:self.PHOTO_LIMIT]]
            }
            if user.id != user_id:
                result['follow'] = user.follower.filter(from_user_id=user_id, status=True).exists()
            else:
                result['follow'] = 'self'
            return JsonResponse({'data':result}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message':'NON_EXISTING_USER'}, status=401)

class UploadView(View):
    @login_check
    def post(self, request, user_id):
        try:
            if user_id:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id     = AWS_S3['access_key'],
                    aws_secret_access_key = AWS_S3['secret_access_key']
                )
                url_id = str(uuid.uuid4().int)
                s3_client.upload_fileobj(
                    request.FILES['filename'],
                    'weplash',
                    url_id,
                    ExtraArgs = {"ContentType":request.FILES['filename'].content_type}
                )
                data  = request.POST.dict()
                image = Image.open(urlopen(AWS_S3['url']+url_id))
                with transaction.atomic():
                    photo = Photo.objects.create(
                        user_id  = user_id,
                        image    = AWS_S3['url']+url_id,
                        location = data['location'],
                        width    = image.width,
                        height   = image.height
                    )
                    if HashTag.objects.filter(name=data['location']).exists():
                        hashtag = HashTag.objects.get(name=data['location'])
                    else:
                        hashtag = HashTag.objects.create(
                            name = data['location']
                        )
                    PhotoHashTag.objects.create(
                        photo   = photo,
                        hashtag = hashtag
                    )
                    PhotoCollection.objects.create(
                        photo = photo,
                        collection = Collection.objects.get(
                            user = User.objects.get(user_name='weplash'),
                            name = data['category']
                        )
                    )
                upload_image.delay(photo.image)
                return HttpResponse(status=200)
            return JsonResponse({'message':'UNAUTHORIZED'}, status=401)
        except KeyError:
            return JsonResponse({'message':"KEY_ERROR"}, status=400)

class PhotoView(View):
    @login_check
    def get(self,request,user_id):
        try:
            query = Q()
            offset        = int(request.GET.get('offset', 0))
            limit         = int(request.GET.get('limit', 20))
            category      = request.GET.get('category',None)
            user          = request.GET.get('user',None)
            user_category = request.GET.get('user_category',None)
            hashtag       = request.GET.get('search',None)
            if category:
                if category == 'Photo':
                    pass
                elif category == 'Following':
                    if Follow.objects.filter(from_user_id=user_id).exists():
                        query &= (Q(user__follower__from_user_id    = user_id,
                                    user__follower__status          = True))
                    else:
                        return JsonResponse({"data" : []}, status=200)
                else:
                    query &= (Q(collection__user__user_name ='weplash',
                                collection__name            = category))
            elif user:
                if user_category == 'photos':
                    query &= (Q(user__user_name=user))
                elif user_category == 'likes':
                    query &= (Q(like__user__user_name=user))
                else:
                    query &= (Q(collection__user__user_name = user,
                                collection__name            = user_category))
            elif not user:
                if user_category == 'photos':
                    query &= (Q(user__id = user_id))
                elif user_category == 'likes':
                    query &= (Q(like__user__id = user_id))
                else:
                    query &= (Q(collection__user__id    = user_id,
                                collection__name        = user_category))

            elif hashtag:
                query &= (Q(hashtag__name  = hashtag))

            photos = Photo.objects.filter(query).prefetch_related("user").order_by('-id')

            likes = set(Like.objects.filter(
                user_id = user_id,
                status  = True, photo__in = list(photos)
            ).values_list('photo_id', flat=True))

            collections = set(PhotoCollection.objects.filter(
                collection__user_id = user_id,
                photo__in           = list(photos)
            ).values_list('photo_id', flat=True))

            data = [{
                "id"                 : photo.id,
                "image"              : photo.image,
                "location"           : photo.location,
                "user_first_name"    : photo.user.first_name,
                "user_last_name"     : photo.user.last_name,
                "user_profile_image" : photo.user.profile_image,
                "user_name"          : photo.user.user_name,
                "width"              : photo.width,
                "height"             : photo.height,
                "user_like"          : True if photo.id in likes else False,
                "user_collection"    : True if photo.id in collections else False
            } for photo in photos[offset*limit:(offset+1)*limit]]
            return JsonResponse({"data":data},status=200)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=400)

class CollectionMainView(View):
    def get(self,request):
        try:
            category = request.GET.get('category',None)
            collection = Collection.objects.get(name=category, user=User.objects.get(user_name='weplash'))
            user = User.objects.filter(photo__photocollection__collection = Collection.objects.get(user=User.objects.get(user_name='weplash'),name='Nature')).distinct().annotate(count=Count('photo__id'))
            result = [{
                    "collection"      : collection.name,
                    "description"     : collection.description,
                    "contributions"   : collection.photocollection_set.all().aggregate(Count('id'))['id__count'],
                    "topcontributors" : list(user.order_by('-count')[:5].values('id', 'profile_image'))
            }]
            return JsonResponse({"data":result},status=200)
        except Collection.DoesNotExist:
            return JsonResponse({'message' : "NON_EXISTING_COLLECTION"}, status=401)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)
        except KeyError:
            return JsonResponse({"message":"KEY_ERROR"},status=400)

class BackgroundView(View):
    def get(self,request):
        try:
            query         = Q()
            offset        = int(request.GET.get('offset', 0))
            limit         = int(request.GET.get('limit', 20))
            category      = request.GET.get('category',None)
            user          = request.GET.get('user',None)
            user_category = request.GET.get('user_category',None)
            hashtag       = request.GET.get('search',None)
            if category:
                query &= (Q(collection__user__user_name='weplash', collection__name=category))
            elif user:
                if user_category == 'photos':
                    query &= (Q(user__user_name=user))
                elif user_category == 'likes':
                    query &= (Q(like__user__user_name=user))
                else:
                    query &= (Q(collection__user__user_name=user, collection__name=user_category))
            elif hashtag:
                query.add(Q(hashtag = HashTag.objects.get(
                    name = hashtag
                )),query.AND)

            photos = Photo.objects.filter(query).prefetch_related("user","background_color")
            data = [{
                "id"                : photo.id,
                "background_color"  : photo.background_color.name,
                "width"             : photo.width,
                "height"            : photo.height
            }for photo in photos[offset*limit:(offset+1)*limit]]
            return JsonResponse({"data":data},status=200)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)
        except KeyError:
            return JsonResponse({'message' : "KEY_ERROR"}, status=400)

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

            result = cache.get(f'user_{user_name}')
            if not result:
                result = {
                    "id"                    : user.id,
                    "user_first_name"       : user.first_name,
                    "user_last_name"        : user.last_name,
                    "user_name"             : user.user_name,
                    "user_profile_image"    : user.profile_image,
                    "photos"                : list(user.photo_set.filter().values_list('image', flat=True))[:self.PHOTO_LIMIT],
                }
                cache.set(f'user_{user_name}', result)

            if result['id'] != user_id:
                result['follow'] = user.follower.filter(from_user_id=user_id, status=True).exists()
            else:
                result['follow'] = 'self'
            return JsonResponse({'data' : result}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'message' : 'NON_EXISTING_USER'}, status=401)

class LikePhotoView(View):
    @login_check
    def patch(self, request, user_id):
        try:
            data  = json.loads(request.body)
            photo = Photo.objects.get(id=data['photo_id'])
            user  = User.objects.get(id=user_id)
            if Like.objects.filter(photo_id=photo.id, user_id=user.id).exists():
                like        = Like.objects.get(photo_id=photo.id, user_id=user.id)
                like.status = not like.status
                like.save()
                return JsonResponse({'user_like':like.status}, status=200)
            like = Like.objects.create(
                photo_id = photo.id,
                user_id  = user.id,
            )
            return JsonResponse({'user_like':like.status}, status=200)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

class RelatedPhotoBackColorView(View):
    def get(self, request, photo_id):
        try:
            offset       = request.GET.get('offset', 0)
            limit        = request.GET.get('limit', 20)
            related_tags = list(HashTag.objects.filter(photo__id=photo_id).values_list('name', flat=True))
            photos       = Photo.objects.filter(hashtag__name__in=related_tags).exclude(id=photo_id).distinct()
            data         = [{
                "id"               : photo.id,
                "background_color" : photo.background_color.name,
                "width"            : photo.width,
                "height"           : photo.height
            } for photo in photos[offset*limit:(offset+1)*limit]]
            return JsonResponse({"data":data},status=200)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)
        except Photo.DoesNotExist:
            return JsonResponse({"message":"NON_EXISTING_PHOTO"},status=400)

class ModalCollectionView(View):
    @login_check
    def get(self, request, user_id, photo_id):
        try:
            user_collection = Collection.objects.select_related('user').prefetch_related('photo_set').filter(user_id=user_id)
            collection_list = [{
                'collection_name' : collection_obj.name,
                'first_image'     : collection_obj.photo_set.first().image if collection_obj.photo_set.exists() else False,
                'photo_count'     : collection_obj.photo_set.count(),
                'private_status'  : collection_obj.private,
                'photo_exist'     : collection_obj.photo_set.filter(id=photo_id).exists()
            } for collection_obj in user_collection]
            return JsonResponse({'data':collection_list}, status=200)
        except Exception as e:
            return JsonResponse({'message':e}, status=400)

class AddCollectionView(View):
    @login_check
    def post(self, request, user_id):
        try:
            data                 = json.loads(request.body)
            photo_id             = data['photo_id']
            collection_name      = data['collection_name']
            user_pick_collection = Collection.objects.get(name=collection_name, user__id=user_id)
            if PhotoCollection.objects.filter(photo_id=photo_id, collection_id=user_pick_collection.id).exists():
                PhotoCollection.objects.filter(photo_id=photo_id, collection_id=user_pick_collection.id).delete()
                user_collections = Collection.objects.filter(user_id=user_id)
                collection_list  = [{
                    'collection_name' : collection_obj.name,
                    'first_image'     : collection_obj.photo_set.first().image if collection_obj.photo_set.exists() else False,
                    'photo_count'     : collection_obj.photo_set.count(),
                    'private_status'  : collection_obj.private,
                    'photo_exist'     : PhotoCollection.objects.filter(photo_id=photo_id, collection_id=collection_obj.id).exists()
                } for collection_obj in user_collections]
                return JsonResponse({'data':collection_list}, status=200)
            PhotoCollection.objects.create(
                photo_id      = photo_id,
                collection_id = user_pick_collection.id
            )
            user_collections = Collection.objects.filter(user_id=user_id)
            collection_list  = [{
                'collection_name' : collection_obj.name,
                'first_image'     : collection_obj.photo_set.first().image if collection_obj.photo_set.exists() else False,
                'photo_count'     : collection_obj.photo_set.count(),
                'private_status'  : collection_obj.private,
                'photo_exist'     : PhotoCollection.objects.filter(photo_id=photo_id, collection_id=collection_obj.id).exists()
            } for collection_obj in user_collections]
            return JsonResponse({'data':collection_list}, status=200)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

class CreateCollectionView(View):
    @login_check
    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            photo_id                  = data['photo_id']
            collection_name           = data['name']
            collection_description    = data['description']
            collection_private_status = data['private']
            if Collection.objects.filter(name=collection_name).exists():
                return JsonResponse({'message':'Another collection is already using this name.'}, status=400)
            collection = Collection.objects.create(
                user_id     = user_id,
                name        = collection_name,
                description = collection_description,
                private     = collection_private_status
            )
            PhotoCollection.objects.create(
                photo_id = photo_id,
                collection_id = collection.id
            )
            user_collection  = Collection.objects.select_related('user').prefetch_related('photo_set').filter(user_id=user_id)
            collection_list  = [{
                'collection_name' : collection_obj.name,
                'first_image'     : collection_obj.photo_set.first().image if collection_obj.photo_set.exists() else False,
                'photo_count'     : collection_obj.photo_set.count(),
                'private_status'  : collection_obj.private,
                'photo_exist'     : collection_obj.photo_set.filter(id=photo_id).exists()
            } for collection_obj in user_collection]
            return JsonResponse({'data':collection_list}, status=200)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

class SearchTagView(View):
    def get(self, request):
        tag = request.GET.get('search',None)
        tags = list(HashTag.objects.filter(photo__hashtag__name = tag).values_list("name")[:10])
        return JsonResponse({"data":tags},status=200)
