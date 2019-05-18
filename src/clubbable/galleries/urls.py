from django.conf.urls import url
from galleries.views import (
    ImageList,
    show,
    download_display,
    download_original,
    download_thumbnail,
)

urlpatterns = [
    url(r'^(?P<gallery_id>\d+)/$', ImageList.as_view(), name='image_list'),
    url(r'^(?P<gallery_id>\d+)/(?P<pk>\d+)/$', show, name='image_show'),
    url(r'^(?P<gallery_id>\d+)/(?P<pk>\d+)/original/(?P<filename>[^/]+)$',
        download_original, name='download_original'),
    url(r'^(?P<gallery_id>\d+)/(?P<pk>\d+)/thumbnail/(?P<filename>[^/]+)$',
        download_thumbnail, name='download_thumbnail'),
    url(r'^(?P<gallery_id>\d+)/(?P<pk>\d+)/display/(?P<filename>[^/]+)$',
        download_display, name='download_display'),
]
