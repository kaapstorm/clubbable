"""
Adds tiles to the dashboard
"""
from django.template import loader


def get_tiles(request):
    """
    Return HTML tiles for the dashboard
    """
    if request.user.is_staff:
        template = loader.get_template('import_mdb/tile.html')
        return [template.render()]
    return []
