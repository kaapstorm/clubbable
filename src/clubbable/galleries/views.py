from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from galleries.models import Gallery, Image
from club.views import get_context_data, ClubbableContextMixin


class ImageList(LoginRequiredMixin, ListView, ClubbableContextMixin):
    context_object_name = 'images'
    paginate_by = 96
    allow_empty = False

    def get_gallery(self):
        return get_object_or_404(Gallery, pk=self.kwargs['gallery_id'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['gallery'] = self.get_gallery()
        return context_data

    def get_queryset(self):
        return self.get_gallery().image_set.all()


@login_required
def show(request, gallery_id, pk):
    context_data = get_context_data(request)
    context_data['image'] = get_object_or_404(Image, pk=pk)
    return render(request, 'galleries/show_image.html', context_data)


@login_required
def download(request, gallery_id, pk, filename):
    image = get_object_or_404(Image, pk=pk)
    return FileResponse(image.original, as_attachment=True)
