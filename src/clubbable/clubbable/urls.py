from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.urls import path, include
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
    path('accounts/', include(auth_urls)),
    path('admin/', admin.site.urls),
]
