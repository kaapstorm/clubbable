from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from markdown import markdown

from club.views import ClubbableContextMixin
from pages.models import Page


class PageView(TemplateView, ClubbableContextMixin):
    template_name = 'pages/page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = get_object_or_404(Page, index=kwargs['index'])
        context.update({'page': page})
        return context


class LandingView(PageView, LoginView):

    def get_context_data(self, **kwargs):
        return super().get_context_data(index=0, **kwargs)
