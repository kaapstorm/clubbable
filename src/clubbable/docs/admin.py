from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from docs.models import Folder, Document


class FromDropboxListFilter(admin.SimpleListFilter):
    title = _('Dropbox')
    parameter_name = 'dropbox'

    def lookups(self, request, model_admin):
        return (
            ('True', _('Yes')),
            ('False', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.exclude(dropbox_file_id__exact='')
        if self.value() == 'False':
            return queryset.filter(dropbox_file_id__exact='')


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'folder', 'from_dropbox')
    list_filter = ('folder', FromDropboxListFilter)
    search_fields = ('description',)

    def from_dropbox(self, obj):
        return bool(obj.dropbox_file_id)
    from_dropbox.short_description = 'Dropbox'
    from_dropbox.boolean = True


admin.site.register(Folder)
admin.site.register(Document, DocumentAdmin)
