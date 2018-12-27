from django import forms

class UploadMdbForm(forms.Form):
    access_db = forms.FileField()
