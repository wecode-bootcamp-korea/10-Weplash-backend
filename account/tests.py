from django.test import (
    TestCase,
    Client
)

from .models import (
    User,
    UserInterest,
    Like
)
from photo.models import (
    HashTag,
    Photo
)

class ProfileViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id         = 5,
            first_name = 'first',
            last_name  = 'last',
            user_name  = 'testuser',
            password   = '123456',
            email      = 'test@test.com'
        )
        HashTag.objects.create(
            id   = 1,
            name = 'animal'
        )
        UserInterest.objects.create(
            id       = 1,
            user     = User.objects.get(id = 5),
            interest = HashTag.objects.get(id = 1)
        )

    def tearDown(self):
        User.objects.all().delete()
        HashTag.objects.all().delete()
        UserInterest.objects.all().delete()

    def test_profileview_success(self):
        client = Client()
        header = {"HTTP_Authorization" : 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1fQ.HMyvGoHsfw2Yhjuy41_pnMCiIBdk1_1rigu72kfmnOM'
}
        response = client.get('/account/@testuser', content_type='application/json', **header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'user' : True,
            'data' : {
                'first_name'    : 'first',
                'last_name'     : 'last',
                'profile_image' : None,
                'interests'     : ['animal']
            }
        })

    def test_profileview_success_2(self):
        client = Client()
        response = client.get('/account/@testuser')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'user' : False,
            'data' : {
                'first_name' : 'first',
                'last_name' : 'last',
                'profile_image' : None,
                'interests' : ['animal']
            }
        })

    def test_profileview_fail(self):
        client = Client()
        response = client.get('/account/@test')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message' : 'NON_EXISTING_USER'})

