from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.base import ContextMixin

from club.models import Member


def get_context_data(request):
    try:
        user_full_name = request.user.get_full_name()
    except AttributeError:
        # Even AnonymousUser has get_username()
        user_full_name = request.user.get_username()
    return {
        'club_name': settings.CLUB_NAME,
        'user_full_name': user_full_name,
    }


class ClubbableContextMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data(self.request))
        return context


class MemberList(LoginRequiredMixin, ListView, ClubbableContextMixin):
    model = Member
    context_object_name = 'members'
    paginate_by = 100


class MemberProfile(LoginRequiredMixin, DetailView, ClubbableContextMixin):
    model = Member
    context_object_name = 'member'


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
    context = get_context_data(request)
    context.update({
        'tiles': _get_tiles(request),
    })
    return render(request, 'club/dashboard.html', context)
