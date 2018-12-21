from django.db import models
from club.models import GetOrNoneManager, User


class DropboxUser(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    account = models.CharField(max_length=255, blank=True, db_index=True)
    access_token = models.CharField(max_length=255, blank=True)
    is_locked = models.BooleanField(default=False)

    objects = GetOrNoneManager()
