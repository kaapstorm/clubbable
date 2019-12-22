from django.contrib import admin

from pages.forms import PageForm
from pages.models import Page


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'index')
    form = PageForm


admin.site.register(Page, PageAdmin)
