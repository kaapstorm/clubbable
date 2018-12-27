from django.conf.urls import url
from dropboxer.views import *

urlpatterns = [
    url(r'^check/$', check_dropbox, name='check_dropbox'),
    url(r'^connect/$', dropbox_auth_start, name='dropbox_auth_start'),
    url(r'^auth/$', dropbox_auth_finish, name='dropbox_auth_finish'),
    url(r'^logout/$', dropbox_logout, name='dropbox_logout'),
    url(r'^webhook/$', webhook, name='dropbox_webhook'),
]
