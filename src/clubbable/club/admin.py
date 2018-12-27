from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from club.models import Member, Profile, User, Guest


class UserAdmin(UserAdminBase):
    """
    UserAdmin class replaces username with email
    """
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
    list_display = ('__str__', 'year', 'email', 'receives_emails')
    list_filter = ('receives_emails', 'year')
    search_fields = ('last_name', 'email')
    inlines = [
        ProfileInline,
    ]


class GuestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_of_listing', 'admitted_to_club')
    list_filter = ('admitted_to_club',)
    search_fields = ('last_name',)


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Member, MemberAdmin)
admin.site.register(Guest, GuestAdmin)
