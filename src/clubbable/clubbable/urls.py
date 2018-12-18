from django.conf import settings
from django.contrib import admin
from django.contrib.auth import urls as auth_urls, views as auth_views
from django.urls import path, include
from markdown import markdown
import yaml
from docs import urls as docs_urls
from galleries import urls as galleries_urls
from dropboxer import urls as dropbox_urls
from website.views import dashboard


def _get_login_context():
    with open(settings.BASE_DIR + '/clubbable/landing_page.yaml') as file:
        data = yaml.load(file)
    return {
        'club_name': settings.CLUB_NAME,
        'heading': data['heading'],
        'image': data['image'],
        'content_html': markdown(data['content_markdown']),
    }


# Replace the login url with out own definition that includes the context for
# the landing page
auth_urls.urlpatterns[0] = path(
    'login/',
    auth_views.LoginView.as_view(),
    {'extra_context': _get_login_context()},
    name='login'
)

admin.autodiscover()

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('doc/', include(docs_urls)),
    path('img/', include(galleries_urls)),
    path('dropbox/', include(dropbox_urls)),

    path('accounts/', include(auth_urls)),
    path('admin/', admin.site.urls),
]
