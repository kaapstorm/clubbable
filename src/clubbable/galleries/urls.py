from django.conf.urls import url
from galleries.views import *

urlpatterns = [
    url(r'^(?P<gallery_id>\d+)/$', ImageList.as_view(), name='image_list'),
]
