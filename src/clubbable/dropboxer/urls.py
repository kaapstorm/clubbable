from django.conf.urls import url
from dropboxer.views import *

urlpatterns = [
    url(r'^check/$', check_dropbox, name='check_dropbox'),
    url(r'^connect/$', connect, name='dropbox_connect'),
    url(r'^auth/$', auth, name='dropbox_auth'),
    url(r'^logout/$', dropbox_logout, name='dropbox_logout'),
    url(r'^webhook/$', webhook, name='dropbox_webhook'),
]
