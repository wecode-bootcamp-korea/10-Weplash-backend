import bcrypt, json, jwt, os, requests, sys, re

from django.views           import View
from django.http            import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models       import Q

from auth           import login_check
from my_settings    import SECRET_KEY, ALGORITHM
from photo.models   import Photo
from account.models import (
    User,
    UserInterest,
    Follow
)

def validation_user_name(user_name):
    check = re.search('\W|\s', user_name)
    if check:
        return False
    elif len(user_name) == 0:
        return False
    return True

def validation_password(password):
    if len(password) > 5:
        return True
    return False

class SignUpView(View):
    default_profile_url = 'https://images.unsplash.com/placeholder-avatars/extra-large.jpg?dpr=1&auto=format&fit=crop&w=150&h=150&q=60&crop=faces&bg=fff'
    def post(self, request):
        data = json.loads(request.body)
        try:
            vu = validation_user_name(data['user_name'])
            validate_email(data['email'])
            vp = validation_password(data['password'])
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'message':'THIS EMAIL ALREADY EXISTS'}, status=400)
            if User.objects.filter(user_name=data['user_name']).exists():
                return JsonResponse({'message':'THIS USER NAME ALREADY EXISTS'}, status=400)
            elif vu and vp:
                user = User.objects.create(
                    first_name    = data['first_name'],
                    last_name     = data['last_name'],
                    user_name     = data['user_name'],
                    email         = data['email'],
                    password      = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    profile_image = self.default_profile_url,
                    is_active     = False
                )
                access_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')
                return JsonResponse({'access_token':access_token}, status=200)
            return JsonResponse({'message':'VALIDATION_ERROR'}, status=400)
        except ValidationError:
            return JsonResponse({'message':'VALIDATION_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

class SignInView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            email    = data['email']
            password = data['password']
            validate_email(email)
            if validation_password(password) and User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    access_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')
                    return JsonResponse({'access_token':access_token}, status=200)
            return JsonResponse({'message':'VALIDATION_ERROR'}, status=400)
        except ValidationError:
            return JsonResponse({'message':'VALIDATION_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)

class KakaoSignInView(View):
    default_profile_url = 'https://images.unsplash.com/placeholder-avatars/extra-large.jpg?dpr=1&auto=format&fit=crop&w=150&h=150&q=60&crop=faces&bg=fff'
    def post(self, request):
        try:
            data                = json.loads(request.body)
            kakao_token         = data['access_token']
            response_from_kakao = requests.get('https://kapi.kakao.com/v2/user/me', headers={'Authorization':f'Bearer {kakao_token}'})
            user_info_data      = response_from_kakao.json()
            kakao_id            = str(user_info_data['id'])
            kakao_account       = user_info_data['kakao_account']
            name                = kakao_account['profile']['nickname']
            email               = kakao_account['email']
            user_name           = email.split('@')[0]
            validate_email(email)
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if bcrypt.checkpw(kakao_id.encode('utf-8'), user.password.encode('utf-8')):
                    access_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')
                    return JsonResponse({'access_token':access_token}, status=200)
            user = User.objects.create(
                first_name = name[1:],
                last_name  = name[0],
                user_name  = user_name,
                email      = email,
                password   = bcrypt.hashpw(kakao_id.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                profile_image = self.default_profile_url,
                is_active     = False
            )
            access_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM).decode('utf-8')
            return JsonResponse({'access_token':access_token}, status=200)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        except ValidationError:
            return JsonResponse({'message':'VALIDATION_ERROR'}, status=400)

class ProfileView(View):
    @login_check
    def get(self, request, user_id):
        user_page = request.GET.get('user', None)
        user_name = request.GET.get('user_name', None)
        query = Q()

        if user_page:
            if user_id:
                query &= Q(id=user_id)
            else:
                return JsonResponse({"message": "UNAUTHORIZED"}, status=401)
        elif user_name:
            if User.objects.filter(user_name=user_name).exists():
                query &= Q(user_name=user_name)
            else:
                return JsonResponse({"message" : 'NON_EXISTING_USER'}, status=401)

        user = User.objects.filter(query).prefetch_related("interest").first()
        data = {
            'first_name'    : user.first_name,
            'last_name'     : user.last_name,
            'profile_image' : user.profile_image,
            'interests'     : list(user.interest.values_list('name', flat=True))
        }
        if user_id:
            if user.id == user_id:
                return JsonResponse({'user' : True, 'data' : data}, status=200)
            elif user_page:
                return JsonResponse({'user' : True, 'data' : data}, status=200)
            return JsonResponse({'user' : False, 'data' : data}, status=200)
        return JsonResponse({'user' : False, 'data' : data}, status=200)

class FollowingView(View):
    @login_check
    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            if User.objects.filter(id=data['user_id']):
                if Follow.objects.filter(from_user_id=user_id, to_user_id=data['user_id']).exists():
                    follow = Follow.objects.get(from_user_id=user_id, to_user_id=data['user_id'])
                    if follow.status:
                        follow.status = False
                        follow.save()
                    else:
                        follow.status = True
                        follow.save()
                else:
                    follow = Follow.objects.create(
                        from_user_id = user_id,
                        to_user_id   = data['user_id']
                    )
                    return JsonResponse({'status':follow.status}, status=200)
                return JsonResponse({'status':follow.status}, status=200)
            return JsonResponse({'message':'INVALID_USER'}, status=401)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status=400)
