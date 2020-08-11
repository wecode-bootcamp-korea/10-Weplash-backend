from django.test import (
    TestCase,
    Client
)

from account.models import (
    User,
    Collection
)
from .models import (
    Photo,
    HashTag,
    PhotoHashTag,
    PhotoCollection
)

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
                "user_profile_image" : None
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
                email      = 'test@test.com'
                ),
                User(
                id         = 2,
                first_name = 'we',
                last_name  = 'plash',
                user_name  = 'weplash',
                email      = 'test2@test.com'
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
