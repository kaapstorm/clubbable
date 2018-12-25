import yaml
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from markdown import markdown
from club.utils import get_full_name


class LandingView(LoginView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with open(settings.BASE_DIR + '/clubbable/landing_page.yaml') as file:
            data = yaml.load(file)
        context.update({
            'club_name': settings.CLUB_NAME,
            'heading': data['heading'],
            'image': data['image'],
            'content_html': markdown(data['content_markdown']),
        })
        return context


def _get_tiles(request):
    """
    Return tiles from all dashboard apps
    """
    tiles = []
    for app in settings.INSTALLED_APPS:
        try:
            module = __import__(app + '.dashboard')
            tiles.extend(module.dashboard.get_tiles(request))
        except (ImportError, AttributeError):
            # If the app doesn't have dashboard.get_tiles(), just
            # move along.
            continue
    return tiles


@login_required
def dashboard(request):
    context = {
        'full_name': get_full_name(request.user),
        'tiles': _get_tiles(request),
    }
    return render(request, 'website/dashboard.html', context)
