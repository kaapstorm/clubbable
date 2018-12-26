from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from club.models import Member, Profile, User


class UserAdmin(UserAdminBase):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class ProfileInline(admin.TabularInline):
    model = Profile


class MemberAdmin(admin.ModelAdmin):
    inlines = [
        ProfileInline,
    ]


admin.site.register(User, UserAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Profile)
