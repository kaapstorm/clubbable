from django.contrib import admin
from club.models import Member, Profile


class ProfileInline(admin.TabularInline):
    model = Profile


class MemberAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline,
    ]


admin.site.register(Member, MemberAdmin)
admin.site.register(Profile)
