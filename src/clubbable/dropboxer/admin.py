from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from dropboxer.models import DropboxUser


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


class DropboxAdminBase(admin.ModelAdmin):

    def from_dropbox(self, obj):
        return bool(obj.dropbox_file_id)
    from_dropbox.short_description = 'Dropbox'
    from_dropbox.boolean = True


class DropboxUserAdmin(admin.ModelAdmin):
    fields = ('user', 'account', 'has_access_token', 'has_cursor', 'is_locked')
    readonly_fields = ('user', 'account', 'has_access_token', 'has_cursor')

    def has_access_token(self, obj):
        return bool(obj.access_token)
    has_access_token.boolean = True

    def has_cursor(self, obj):
        return bool(obj.cursor)
    has_cursor.boolean = True


admin.site.register(DropboxUser, DropboxUserAdmin)
