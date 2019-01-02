"""
Adds tiles to the dashboard
"""
from django.template import loader


def get_tiles(request):
    """
    Return HTML tiles for the dashboard
    """
    template = loader.get_template('website/members_tile.html')
    tile = template.render()
    return [tile]
