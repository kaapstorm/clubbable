from django.urls import path
from mailer.views import send


urlpatterns = [
    path('send/', send, name='message_send'),
]
