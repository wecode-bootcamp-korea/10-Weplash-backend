import json

from django.db.models import Q
import json
from django.test import (
    TestCase,
    Client
)

from django.core.files.uploadedfile import SimpleUploadedFile

from account.models import (
    User,
    Like,
    Interest,
    UserInterest,
    Follow,
    Collection
)

from .models import (
    Photo,
    HashTag,
    PhotoHashTag,
    PhotoCollection,
    BackGroundColor
)

import unittest

class RelatedPhotoViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id         = 1,
            first_name = 'first',
            last_name  = 'last',
            user_name  = 'test'
        )
        Photo.objects.bulk_create([
            Photo(
                id       = 1,
                user     = User.objects.get(id = 1),
                image    = 'image',
                location = 'location'
            ),
            Photo(
                id       = 2,
                user     = User.objects.get(id = 1),
                image    = 'image',
                location = 'location'
            )])
        HashTag.objects.create(
            id   = 1,
            name = 'tag'
        )
        PhotoHashTag.objects.bulk_create([
            PhotoHashTag(
                id      = 1,
                photo   = Photo.objects.get(id = 1),
                hashtag = HashTag.objects.get(id = 1)
            ),
            PhotoHashTag(
                id      = 2,
                photo   = Photo.objects.get(id = 2),
                hashtag = HashTag.objects.get(id = 1)
            )])

    def tearDown(self):
        User.objects.all().delete()
        Photo.objects.all().delete()
        HashTag.objects.all().delete()
        PhotoHashTag.objects.all().delete()

    def test_relatedphotoview_success(self):
        client = Client()
        response = client.get('/photo/related-photo/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "tags" : ["tag"],
            "data" : [{
                "id"                 : 2,
                "image"              : "image",
                "location"           : "location",
                "user_first_name"    : "first",
                "user_last_name"     : "last",
                "user_name"          : "test",
                "user_profile_image" : None,
                "user_like"          : False,
                "user_collection"    : False
            }]})

    def test_relatedphotoview_fail(self):
        client = Client()
        response = client.get('/photo/related-photo/3')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            "message" : "NON_EXISTING_PHOTO"
        })

    def test_relatedphotoview_exception(self):
        client = Client()
        response = client.get('/photo/related-photo/test')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "INVALID_PHOTO"})

class RelatedCollectionViewTest(TestCase):
    def setUp(self):
        User.objects.bulk_create([
            User(
                id         = 1,
                first_name = 'first',
                last_name  = 'last',
                user_name  = 'test',
                password   = 1234567
                email      = 'test@test.com'
                ),
                User(
                id         = 2,
                first_name = 'we',
                last_name  = 'plash',
                user_name  = 'weplash',
                email      = 'test2@test.com',
                password   = 1234567
                )])
        Photo.objects.create(
            id       = 1,
            image    = 'image',
            location = 'location'
        )
        HashTag.objects.create(
            id   = 1,
            name = 'tag'
        )
        PhotoHashTag.objects.create(
            id      = 1,
            photo   = Photo.objects.get(id = 1),
            hashtag = HashTag.objects.get(id = 1)
        )
        Collection.objects.create(
            id      = 1,
            name    = 'collection',
            user    = User.objects.get(id=1)
        )
        PhotoCollection.objects.create(
            id          = 1,
            photo       = Photo.objects.get(id=1),
            collection  = Collection.objects.get(id=1)
        )

    def tearDown(self):
        User.objects.all().delete()
        Photo.objects.all().delete()
        HashTag.objects.all().delete()
        PhotoHashTag.objects.all().delete()
        Collection.objects.all().delete()
        PhotoCollection.objects.all().delete()

    def test_relatedcollectionview_success(self):
        client = Client()
        response = client.get('/photo/related-collection?photo=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "data" : [
                {
                    "id"              : 1,
                    "image"           : ["image"],
                    "name"            : "collection",
                    "photos_number"   : 1,
                    "user_first_name" : "first",
                    "user_last_name"  : "last",
                    "tags"            : [
                        "tag"
                    ]
                }
            ]
        })

    def test_relatedcollectionview_fail(self):
        client = Client()
        response = client.get('/photo/related-collection?photo=2')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            "message" : "NON_EXISTING_PHOTO"
        })

    def test_relatedcollectionview_exception(self):
        client = Client()
        response = client.get('/photo/related-collection?photo=test')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "INVALID_KEY"})

class SearchBarViewTest(TestCase):
    def setUp(self):
        HashTag.objects.create(id=1, name='test')

    def tearDown(self):
        HashTag.objects.all().delete()

    def test_searchbarview_success(self):
        client = Client()
        response = client.get('/photo/search')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data" : ["test"]})


class UserCardVIewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id          = 1,
            first_name  = 'first',
            last_name   = 'last',
            user_name   = 'testuser',
            email       = 'tset@test.com'
        )
        Photo.objects.create(
            id      = 1,
            user    = User.objects.get(id=1),
            image   = 'image'
        )

    def tearDown(self):
        User.objects.all().delete()
        Photo.objects.all().delete()

    def test_usercardview_success(self):
        client = Client()
        response = client.get('/photo/user-card/testuser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "data" : {
                "id" : 1,
                "user_first_name"       : "first",
                "user_last_name"        : "last",
                "user_name"             : "testuser",
                "user_profile_image"    : None,
                "photos"                : ["image"],
                "follow"                : False
            }
        })

    def test_usercardview_fail(self):
        client = Client()
        response = client.get('/photo/user-card/test')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            "message" : "NON_EXISTING_USER"
        })

class UploadViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id = 5,
            first_name='first',
            last_name='last',
            user_name='testuser',
            email='test@test.com',
            password=1234567
        )

    def tearDown(self):
        PhotoHashTag.objects.all().delete()
        HashTag.objects.all().delete()
        BackGroundColor.objects.all().delete()
        Photo.objects.all().delete()

    def test_uploadview_success(self):
        client = Client()
        image_file = SimpleUploadedFile(name='dog.jpeg', content=open('dog.jpeg', 'rb').read(), content_type='image/jpeg')
        header = {"HTTP_Authorization" : 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1fQ.HMyvGoHsfw2Yhjuy41_pnMCiIBdk1_1rigu72kfmnOM'}
        upload_file = {
            'location' : 'test',
            'filename' : image_file
        }
        response = client.post('/photo/upload', upload_file, **header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "SUCCESS"})

    def test_uploadview_fail(self):
        client = Client()
        with open('dog.jpeg') as image:
            upload_file = {
                'location' : None
            }
            response = client.post('/photo/upload', json.dumps(upload_file), content_type='application/json')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json(), {'message' : "UNAUTHORIZED"})

    def test_uploadview_exception(self):
        client = Client()
        header = {"HTTP_Authorization" : 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1fQ.HMyvGoHsfw2Yhjuy41_pnMCiIBdk1_1rigu72kfmnOM'}
        response = client.post('/photo/upload', content_type='application/json', **header)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "KEY_ERROR"})

class PhotoViewTest(TestCase):
    def setUp(self):
        client = Client()
        user = User.objects.create(
            id            = 1,
            first_name    = 'we',
            last_name     = 'plash',
            profile_image = 'url',
            user_name     = 'weplash',
            email         = 'weplash@weplash.com',
            password      = '123456',
        )
        bc = BackGroundColor.objects.create(
            id   = 1,
            name = '#C0C5CC'
        )
        photo = Photo.objects.create(
            id                  = 1,
            user_id             = user.id,
            image               = 'url',
            location            = 'Zermatt, Schweiz',
            width               = 1000,
            height              = 667,
            background_color_id = bc.id
        )
        collection = Collection.objects.create(
            id   = 1,
            user = user,
            name = 'Nature'
        )
        PhotoCollection.objects.create(
            id            = 1,
            photo_id      = photo.id,
            collection_id = collection.id
        )

    def teardown(self):
        Photo.objects.all().delete()
        User.objects.all().delete()
        BackGroundColor.objects.all().delete()
        Collection.objects.all().delete()
        PhotoCollection.objects.all().delete()


    def test_PhotoView_success(self):
        response = self.client.get('/photo?user=weplash&user_category=Nature&offset=0&limit=20')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
        {'data':[{'height'            : 667,
                  'id'                : 1,
                  'image'             : 'url',
                  'location'          : 'Zermatt, Schweiz',
                  'user_first_name'   : 'we',
                  'user_last_name'    : 'plash',
                  'user_name'         : 'weplash',
                  'user_profile_image': 'url',
                  'width': 1000}]})

    def test_PhotoView_success(self):
        response = self.client.get('/photouser=weplash&user_category=Nature&offset=0&limit=20')
        self.assertEqual(response.status_code, 404)

    def test_PhotoView_success(self):
        response = self.client.get('/photo?user=weplash&user_category=Nature&offset=0&limit=20')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
        {'data':[{"message":"VALUE_ERROR"})

class BackgraundViewTest(TestCase):
    def setUp(self):
        client = Client()
        user = User.objects.create(
        id            = 1,
        first_name    = 'we',
        last_name     = 'plash',
        profile_image = 'url',
        user_name     = 'weplasha',
        email         = 'weplash@weplash.com',
        password      = '123456',
        )
        bc = BackGroundColor.objects.create(
            id   = 1,
            name = '#C0C5CC'
        )
        photo = Photo.objects.create(
            id                  = 1,
            user_id             = user.id,
            image               = 'url',
            location            = 'Zermatt, Schweiz',
            width               = 1000,
            height              = 667,
            background_color_id = bc.id
        )
        collection = Collection.objects.create(
            id   = 1,
            user = user,
            name = 'Nature'
        )
        PhotoCollection.objects.create(
            id            = 1,
            photo_id      = photo.id,
            collection_id = collection.id
        )
    def teardown(self):
        Photo.objects.all().delete()
        User.objects.all().delete()
        BackGroundColor.objects.all().delete()
        Collection.objects.all().delete()
        PhotoCollection.objects.all().delete()

    def test_PhotoView_success(self):
        response = self.client.get('/photo/back/Nature')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
        {'data': [{'background_color': '#C0C5CC',
                   'height'          : 667,
                   'id'              : 1,
                   'width'           : 1000}]})

    def test_PhotoView_success(self):
        response = self.client.get('/phot1/back/Nature')
        self.assertEqual(response.status_code, 404)

class UploadViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id = 5,
            first_name='first',
            last_name='last',
            user_name='testuser',
            email='test@test.com',
            password=1234567
        )

    def tearDown(self):
        PhotoHashTag.objects.all().delete()
        HashTag.objects.all().delete()
        BackGroundColor.objects.all().delete()
        Photo.objects.all().delete()


class SearchBarViewTest(TestCase):
    def setUp(self):
        HashTag.objects.create(id=1, name='test')

    def tearDown(self):
        HashTag.objects.all().delete()

    def test_searchbarview_success(self):
        client = Client()
        response = client.get('/photo/search')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"data" : ["test"]})

class UserCardVIewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id          = 1,
            first_name  = 'first',
            last_name   = 'last',
            user_name   = 'testuser',
            email       = 'tset@test.com'
        )
        Photo.objects.create(
            id      = 1,
            user    = User.objects.get(id=1),
            image   = 'image'
        )

    def tearDown(self):
        User.objects.all().delete()
        Photo.objects.all().delete()

    def test_usercardview_success(self):
        client = Client()
        response = client.get('/photo/user-card/testuser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "data" : {
                "id" : 1,
                "user_first_name"       : "first",
                "user_last_name"        : "last",
                "user_name"             : "testuser",
                "user_profile_image"    : None,
                "photos"                : ["image"],
                "follow"                : False
            }
        })

    def test_usercardview_fail(self):
        client = Client()
        response = client.get('/photo/user-card/test')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            "message" : "NON_EXISTING_USER"
        })

class UploadViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id = 5,
            first_name='first',
            last_name='last',
            user_name='testuser',
            email='test@test.com',
            password=1234567
        )

    def tearDown(self):
        PhotoHashTag.objects.all().delete()
        HashTag.objects.all().delete()
        BackGroundColor.objects.all().delete()
        Photo.objects.all().delete()

    def test_uploadview_success(self):
        client = Client()
        image_file = SimpleUploadedFile(name='dog.jpeg', content=open('dog.jpeg', 'rb').read(), content_type='image/jpeg')
        header = {"HTTP_Authorization" : 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1fQ.HMyvGoHsfw2Yhjuy41_pnMCiIBdk1_1rigu72kfmnOM'}
        upload_file = {
            'location' : 'test',
            'filename' : image_file
        }
        response = client.post('/photo/upload', upload_file, **header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message" : "SUCCESS"})

    def test_uploadview_fail(self):
        client = Client()
        with open('dog.jpeg') as image:
            upload_file = {
                'location' : None
            }
            response = client.post('/photo/upload', json.dumps(upload_file), content_type='application/json')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json(), {'message' : "UNAUTHORIZED"})

    def test_uploadview_exception(self):
        client = Client()
        header = {"HTTP_Authorization" : 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1fQ.HMyvGoHsfw2Yhjuy41_pnMCiIBdk1_1rigu72kfmnOM'}
        response = client.post('/photo/upload', content_type='application/json', **header)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"message" : "KEY_ERROR"})

class LikePhotoViewTest(TestCase):
    def test_likepostview_success_already_true(self):
        client = Client()
        header = {
            'Authorization':'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1fQ.HMyvGoHsfw2Yhjuy41_pnMCiIBdk1_1rigu72kfmnOM'
        }
        body = {
            "photo_id":3
        }
        reponse = client.patch('/photo/like', json.dumps(body), content_type='application/json')
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(response.json(), {'status':False})

    def test_likepostview_success_already_false(self):
        client = Client()
        header = {
            'Authorization':'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1fQ.HMyvGoHsfw2Yhjuy41_pnMCiIBdk1_1rigu72kfmnOM'
        }
        body = {
            "photo_id":4
        }
        reponse = client.patch('/photo/like', json.dumps(body), content_type='application/json')
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(response.json(), {'status':True})
