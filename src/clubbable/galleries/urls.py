from django.conf.urls import url
from galleries.views import ImageList, show, download

urlpatterns = [
    url(r'^(?P<gallery_id>\d+)/$', ImageList.as_view(), name='image_list'),
    url(r'^(?P<gallery_id>\d+)/(?P<pk>\d+)/$', show, name='image_show'),
    url(r'^(?P<gallery_id>\d+)/(?P<pk>\d+)/(?P<filename>[^/]+)$', download,
        name='image_download'),
]
