from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from club.utils import get_full_name


@login_required
def dashboard(request):

    def get_tiles():
        """
        Return tiles from all dashboard apps
        """
        tiles_ = []
        for app in settings.INSTALLED_APPS:
            try:
                module = __import__(app + '.dashboard')
                tiles_.extend(module.dashboard.get_tiles(request))
            except (ImportError, AttributeError):
                # If the app doesn't have dashboard.get_tiles(), just
                # move along.
                continue
        return tiles_

    def get_3_per_row(items):
        """
        Arrange items into rows of 3
        """
        rows = []
        row = []
        for i, item in enumerate(items):
            row.append(item)
            if not (i + 1) % 3:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        return rows

    tiles = get_tiles()
    context = {
        'full_name': get_full_name(request.user),
        'rows': get_3_per_row(tiles),
    }
    return render(request, 'website/dashboard.html', context)
