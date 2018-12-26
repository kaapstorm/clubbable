from django.db import models
from club.models import GetOrNoneManager, User


class DropboxUser(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    access_token = models.CharField(max_length=255, blank=True)

    objects = GetOrNoneManager()
