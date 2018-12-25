from django.conf.urls import url
from docs.views import *

urlpatterns = [
    url(r'^(?P<folder_id>\d+)/$', DocList.as_view(), name='doc_list'),
    url(r'^(?P<folder_id>\d+)/(?P<pk>\d+)/(?P<filename>[^/]+)$', download,
        name='doc_download'),
    url(r'^(?P<folder_id>\d+)/(?P<pk>\d+)/send/$', send, name='doc_send'),
]
