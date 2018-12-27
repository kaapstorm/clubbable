from django.urls import path
from import_mdb.views import upload_mdb


urlpatterns = [
    path('', upload_mdb, name='upload_mdb'),
]
