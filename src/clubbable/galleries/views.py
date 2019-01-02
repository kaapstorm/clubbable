from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from galleries.models import Gallery, Image
from website.views import ClubbableContextMixin


class ImageList(LoginRequiredMixin, ListView, ClubbableContextMixin):
    context_object_name = 'images'

    def get_gallery(self):
        return get_object_or_404(Gallery, pk=self.kwargs['gallery_id'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['gallery'] = self.get_gallery()
        return context_data

    def get_queryset(self):
        return self.get_gallery().image_set.all()
