from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from club.models import Member, Profile, User, Guest


class ReceivesEmailsListFilter(admin.SimpleListFilter):
    title = _('receives emails')
    parameter_name = 'receives_emails'

    def lookups(self, request, model_admin):
        return (
            ('True', _('Yes')),
            ('False', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.exclude(profile__member__receives_emails=False)
        if self.value() == 'False':
            return queryset.filter(profile__member__receives_emails=False)


class HasUserListFilter(admin.SimpleListFilter):
    title = _('has user')
    parameter_name = 'has_user'

    def lookups(self, request, model_admin):
        return (
            ('True', _('Yes')),
            ('False', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.exclude(profile__isnull=True)
        if self.value() == 'False':
            return queryset.filter(profile__isnull=True)

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
    list_display = (
        'email', 'first_name', 'last_name', 'receives_emails', 'is_staff',
    )
    list_filter = (
        ReceivesEmailsListFilter, 'is_staff', 'is_superuser', 'is_active',
        'groups',
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('last_name', 'first_name', 'email')


class ProfileInline(admin.TabularInline):
    model = Profile


class MemberAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'year', 'email', 'link_to_user')
    list_select_related = ('profile',)
    list_filter = (HasUserListFilter, 'year')
    search_fields = ('last_name', 'email')
    inlines = [
        ProfileInline,
    ]

    def link_to_user(self, obj):
        try:
            user = obj.profile.user
        except Member.profile.RelatedObjectDoesNotExist:
            return None
        link = reverse("admin:club_user_change", args=[user.id])
        return format_html(f'<a href="{link}">{user}</a>')
    link_to_user.short_description = 'User'


class GuestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_of_listing', 'admitted_to_club')
    list_filter = ('admitted_to_club',)
    search_fields = ('last_name',)


admin.site.register(User, UserAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Guest, GuestAdmin)
