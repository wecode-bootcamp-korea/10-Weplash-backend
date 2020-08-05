from django.db import models

from photo.models import Photo

class User(models.Model):
    first_name    = models.CharField(max_length=50)
    last_name     = models.CharField(max_length=50)
    user_name     = models.CharField(max_length=50)
    email         = models.EmailField(max_length=255)
    password      = models.CharField(max_length=255)
    profile_image = models.URLField(max_length=2000, null=True)
    is_active     = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    user          = models.ManyToManyField('self', through='Follow')

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

class Like(models.Model):
    user  = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    photo = models.ForeignKey('Photo', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'likes'

class Interest(models.Model):
    name = models.CharField(max_length=50)
    user = models.ManyToManyField('User', through='UserInterest')

    class Meta:
        db_table = 'interests'

    def __str__(self):
        return self.name

class UserInterest(models.Model):
    user     = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    interest = models.ForeignKey('Interest', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'users_interests'

class Follow(models.Model):
    from_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='from_user')
    to_user   = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='to_user')
    stauts    = models.BooleanField(default=True)

    class Meta:
        db_table = 'follows'

class Collection(models.Model):
    user        = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    name        = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=500, null=True)
    private     = models.BooleanField(default=False)

    class Meta:
        db_table = 'collections'

    def __str__(self):
        return self.name
