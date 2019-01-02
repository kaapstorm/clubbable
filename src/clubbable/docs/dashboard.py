"""
Adds tiles to the dashboard
"""
from django.template import loader
from docs.models import Folder


def get_tiles(request):
    """
    Return HTML tiles for the dashboard
    """
    tiles = []
    for folder in Folder.objects.all():
        if folder.document_set.first():
            template = loader.get_template('docs/folder_tile.html')
            tiles.append(template.render({'folder': folder}))
    return tiles
