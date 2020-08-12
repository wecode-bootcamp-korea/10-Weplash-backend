from django.db      import models

from account.models import (
    User,
    Collection
)

class Photo(models.Model):
    user             = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image            = models.URLField(max_length = 255)
    location         = models.CharField(max_length = 50, null=True)
    downloads        = models.IntegerField(default=0)
    views            = models.IntegerField(default=0)
    hashtag          = models.ManyToManyField('HashTag', through='PhotoHashTag')
    collection       = models.ManyToManyField(Collection, through ='PhotoCollection')
    background_color = models.ForeignKey('BackGroundColor', on_delete = models.SET_NULL, null=True)
    width            = models.IntegerField(null=True)
    height           = models.IntegerField(null=True)
    

    class Meta:
        db_table = 'photos'

class HashTag(models.Model):
    name = models.CharField(max_length = 50)

    class Meta:
        db_table = 'hashtags'

class PhotoHashTag(models.Model):
    photo   = models.ForeignKey(Photo, on_delete = models.SET_NULL, null = True)
    hashtag = models.ForeignKey(HashTag, on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = 'photos_hashtags'

class PhotoCollection(models.Model):
    photo      = models.ForeignKey(Photo, on_delete = models.SET_NULL, null = True)
    collection = models.ForeignKey(Collection, on_delete = models.SET_NULL, null = True)

    class Meta:
        db_table = 'photos_collections'

class BackGroundColor(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'background_colors'
