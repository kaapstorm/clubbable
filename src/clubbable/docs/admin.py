from django.contrib import admin
from docs.models import Folder, Document
from dropboxer.admin import FromDropboxListFilter, DropboxAdminBase


class DocumentAdmin(DropboxAdminBase):
    list_display = ('__str__', 'folder', 'from_dropbox')
    list_filter = ('folder', FromDropboxListFilter)
    search_fields = ('description',)


admin.site.register(Folder)
admin.site.register(Document, DocumentAdmin)
