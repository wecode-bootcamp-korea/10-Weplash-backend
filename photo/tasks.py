from __future__ import (
    absolute_import,
    unicode_literals
)

import requests

from celery.decorators  import task

from my_settings    import (
    S3_URL,
    IMAGGA
)
from .models        import (
    BackGroundColor,
    Photo,
    HashTag,
    PhotoHashTag
)

@task(name='upload_file', ignore_result=True)
def upload_image(photo_url, data):
    auth_key = IMAGGA['api_key']
    auth_secret = IMAGGA['api_secret']

    get_image_hashtag.delay(photo_url, auth_key, auth_secret)
    get_image_color.delay(photo_url, auth_key, auth_secret)

@task(name='get_image_hashtag', ignore_result=True)
def get_image_hashtag(photo_url, auth_key, auth_secret):
    try:
        response = requests.get(
        'https://api.imagga.com/v2/tags?image_url=%s' % photo_url,
        auth = (auth_key, auth_secret))

        for tag in response.json()['result']['tags']:
            if tag['confidence'] > 30:
                if HashTag.objects.filter(name=tag['tag']['en']).exists():
                    PhotoHashTag.objects.create(
                        photo   = Photo.objects.get(image = photo_url),
                        hashtag = HashTag.objects.get(name=tag['tag']['en'])
                    )
                else:
                    hashtag = HashTag.objects.create(name=tag['tag']['en'])
                    PhotoHashTag.objects.create(
                        photo   = Photo.objects.get(image = photo_url),
                        hashtag = hashtag
                    )
    except KeyError:
        pass

@task(name = 'get_image_color', ignore_result=True)
def get_image_color(photo_url, auth_key, auth_secret):
    photo = Photo.objects.get(image = photo_url)
    try:
        response = requests.get(
            'https://api.imagga.com/v2/colors?image_url=%s' % photo_url,
            auth = (auth_key, auth_secret)
        )

        color = response.json()['result']['colors']['background_colors'][0]['html_code']

        if BackGroundColor.objects.filter(name=color).exists():
            photo.background_color = BackGroundColor.objects.get(name=color)
        else:
            back_ground_color = BackGroundColor.objects.create(name=color)
            photo.background_color = back_ground_color

        photo.save()
    except KeyError:
        pass
