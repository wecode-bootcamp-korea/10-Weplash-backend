import json
import jwt
import requests

from django.http import JsonResponse

from my_settings        import SECRET_KEY, ALGORITHM
from account.models     import User

def login_check(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization')
            if access_token:
                data    = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
                user_id = data['user_id']
                return func(self, request, user_id, *args, **kwargs)
            user_id = None
            return func(self, request, user_id, *args, **kwargs)
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status=400)
    return wrapper

def detoken(request):
    try:
        access_token = request.headers.get('Authorization')
        data         = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
        user         = User.objects.get(id=data['user_id'])
        return user
    except jwt.exceptions.DecodeError:
        return None
    except User.DoesNotExist:
        return None
