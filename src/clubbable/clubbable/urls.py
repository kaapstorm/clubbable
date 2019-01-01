from django.conf import settings
from django.contrib import admin
from django.contrib.auth import (
    urls as auth_urls,
    views as auth_views,
)
from django.urls import path, include, re_path
from django.views.static import serve
from docs import urls as docs_urls
from galleries import urls as galleries_urls
from import_mdb import urls as import_mdb_urls
from dropboxer import urls as dropbox_urls
from website.views import dashboard, LandingView

admin.autodiscover()

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('doc/', include(docs_urls)),
    path('img/', include(galleries_urls)),
    path('dropbox/', include(dropbox_urls)),
    path('import_mdb/', include(import_mdb_urls)),

    path('accounts/login/', LandingView.as_view(), name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(
             template_name='website/logged_out.html'
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
