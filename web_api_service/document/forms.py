from django import forms
from django.core.exceptions import ValidationError
from .models import *
from django.utils.translation import gettext_lazy as _


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'color', 'description', 'is_active']


class FileForm(forms.Form):
    category = forms.Select()
    file_path = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    # fields = ['category', 'document_path']
    #
    # widgets = {
    #     'document_path': forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    # }

    # def save(self, **kwargs):
    #     user = kwargs.pop('user')
    #     instance = super(DocumentForm, self).save(**kwargs)
    #     instance.user = user
    #     instance.save()
    #     return instance
