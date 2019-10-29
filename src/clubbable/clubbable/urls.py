from django.conf import settings
from django.contrib import admin
from django.contrib.auth import (
    urls as auth_urls,
    views as auth_views,
)
from django.urls import path, include, re_path
from django.views.static import serve

from club.views import (
    LandingView,
    dashboard,
)
from club import urls as club_urls
from docs import urls as docs_urls
from dropboxer import urls as dropbox_urls
from galleries import urls as galleries_urls
from import_mdb import urls as import_mdb_urls
from mailer import urls as mailer_urls

admin.autodiscover()

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('member/', include(club_urls)),
    path('doc/', include(docs_urls)),
    path('img/', include(galleries_urls)),
    path('dropbox/', include(dropbox_urls)),
    path('import_mdb/', include(import_mdb_urls)),
    path('message/', include(mailer_urls)),

    path('accounts/login/', LandingView.as_view(), name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(
             template_name='club/logged_out.html'
         ),
         name='logout'),
    path('accounts/', include(auth_urls)),
    path('admin/', admin.site.urls),
]

if settings.DEBUG :
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
