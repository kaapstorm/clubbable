from django.contrib import admin
from galleries.models import Gallery, Image


class ImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'gallery')
    list_filter = ('gallery',)
    search_fields = ('description',)


admin.site.register(Gallery)
admin.site.register(Image, ImageAdmin)
