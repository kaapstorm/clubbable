from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from pages.models import Page


class PageForm(ModelForm):
    class Meta:
        model = Page
        fields = [
            'index',
            'title',
            'banner_img_url',
            'content_markdown',
            # Exclude content_html. It is automatically populated by
            # ``Page.save()``
        ]
        help_texts = {
            'index': _(
                'The order in which pages are organized. If index is 0 then '
                'the page is the landing page.'
            ),
            'content_markdown': _(
                'The content of the page in Markdown format. For more '
                'information about Markdown and syntax, see '
                'http://daringfireball.net/projects/markdown/'
            ),
        }
