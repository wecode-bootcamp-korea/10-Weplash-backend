from django.views import View
from django.http  import JsonResponse

from account.models import (
    User,
    UserInterest,
)
from photo.models   import Photo
from auth           import login_check

class ProfileView(View):
    @login_check
    def get(self, request, user_name, user_id):
        if User.objects.filter(user_name=user_name).exists():
            user = User.objects.filter(user_name=user_name).prefetch_related("interest").first()

            data = {
                'first_name'    : user.first_name,
                'last_name'     : user.last_name,
                'profile_image' : user.profile_image,
                'interests'     : list(user.interest.values_list('name', flat=True))
            }

            if user_id:
                if user.id == user_id:
                    return JsonResponse({'user' : True, 'data' : data}, status=200)
                return JsonResponse({'user' : False, 'data' : data}, status=200)
            return JsonResponse({'user' : False, 'data' : data}, status=200)

        return JsonResponse({'message' : 'NON_EXISTING_USER'}, status=401)

