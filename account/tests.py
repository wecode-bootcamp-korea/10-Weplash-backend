import jwt, json

from my_settings import SECRET_KEY, ALGORITHM
from django.test import (
    TestCase,
    Client
)

from unittest.mock import (
    patch,
    MagicMock
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

class KaKaoSignInViewTest(TestCase):
    @patch('account.views.requests')
    def test_kakao_view_post(self, mocked_requests):
        client = Client()
        class MockedResponse:
            def json(self):
                return {
                    'id':'12345',
                    'kakao_account':{
                        'nickname':'madrid',
                        'email':'mino123@icloud.com'
                    }
                }
        mocked_requests.post = MagicMock(return_value = MockedResponse())
        test = {
            'email':'mino123@icloud.com',
            'password':'12345',
            'nickname':'madrid'
        }
        response = client.post('/account/kakao', json.dumps(test), **{'HTTP_AUTHORIZATION':'1234', 'content_type':'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message':'SUCCESS'})

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

class SignUpTest(TestCase):
    URL = 'url'
    def test_signupview_post_success(self):
        client = Client()
        user = {
            'first_name' : 'minho',
            'last_name'  : 'lee',
            'user_name'  : 'test_minho',
            'email'      : 'asdf@gmail.com',
            'password'   : '123456'
        }
        response = client.post('/account/sign-up', json.dumps(user), content_type='application/json')
        user = User.objects.get(email='asdf@gmail.com')
        access_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'access_token':access_token})

    def test_signupview_post_email_fail(self):
        client = Client()
        User.objects.create(
            first_name    = 'minho',
            last_name     = 'lee',
            user_name     = 'test_minho123',
            email         = 'asdf1@gmail.com',
            password      = '123456',
            profile_image = self.URL
        )
        user = {
            'first_name' : 'minho',
            'last_name'  : 'lee',
            'user_name'  : 'test_minho',
            'email'      : 'asdf1@gmail.com',
            'password'   : '123456'
        }
        response = client.post('/account/sign-up', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'THIS EMAIL ALREADY EXISTS'})

    def test_signupview_post_user_name_fail(self):
        client = Client()
        User.objects.create(
            first_name    = 'minho',
            last_name     = 'lee',
            user_name     = 'test_minho123',
            email         = 'asdf1@gmail.com',
            password      = '123456',
            profile_image = self.URL
        )
        user = {
            'first_name' : 'minho',
            'last_name'  : 'lee',
            'user_name'  : 'test_minho123',
            'email'      : 'asdf@gmail.com',
            'password'   : '123456'
        }
        response = client.post('/account/sign-up', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'THIS USER NAME ALREADY EXISTS'})

    def test_signupview_post_validation_error(self):
        client = Client()
        user = {
            'first_name' : 'minho',
            'last_name'  : 'lee',
            'user_name'  : '@#test_minho#@',
            'email'      : 'asdf@gmail.com',
            'password'   : '123456'
        }
        response = client.post('/account/sign-up', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'VALIDATION_ERROR'})

    def test_signupview_post_key_error(self):
        client = Client()
        user = {
            'first_name' : 'minho',
            'last_name'  : 'lee',
            'username'   : 'test_minho',
            'email'      : 'asdf@gmail.com',
            'password'   : '123456'
        }
        response = client.post('/account/sign-up', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'KEY_ERROR'})
