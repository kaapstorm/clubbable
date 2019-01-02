from django.contrib import admin
from dropboxer.admin import DropboxAdminBase, FromDropboxListFilter
from galleries.models import Gallery, Image


class ImageAdmin(DropboxAdminBase):
    list_display = ('__str__', 'gallery', 'from_dropbox')
    list_filter = ('gallery', FromDropboxListFilter)
    search_fields = ('description',)


admin.site.register(Gallery)
admin.site.register(Image, ImageAdmin)
