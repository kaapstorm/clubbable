from django.urls import path, re_path

from club.views import MemberList, MemberProfile

urlpatterns = [
    path('', MemberList.as_view(), name='member_list'),
    re_path(r'^(?P<pk>\d+)/$', MemberProfile.as_view(),
            name='member_profile'),
]
