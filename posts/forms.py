from django.forms import ModelForm
from django import forms
from .models import Post, Comment, SharedPost
from ckeditor.widgets import CKEditorWidget

class PostModelForm(ModelForm):
    class Meta:
        model = Post
        fields = ['description', 'image', 'privacy']

class SharedPostModelForm(ModelForm):
    class Meta:
        model = SharedPost
        fields = ['quote']


class AddCommentModelForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
