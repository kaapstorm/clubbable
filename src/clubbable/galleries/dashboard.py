"""
Adds tiles to the dashboard
"""
from django.template import loader
from galleries.models import Gallery


def get_tiles(request):
    """
    Return HTML tiles for the dashboard
    """
    tiles = []
    for gallery in Gallery.objects.all():
        if gallery.image_set.first():
            template = loader.get_template('galleries/gallery_tile.html')
            tiles.append(template.render({'gallery': gallery}))
    return tiles
