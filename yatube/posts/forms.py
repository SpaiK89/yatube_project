from django import forms
from django.forms import Textarea
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('hidden_text', 'text',)
        widgets = {
            'text': Textarea(attrs={'rows': 2,
                                    'placeholder': "Оставьте комментарий"}),
            'hidden_text': Textarea(attrs={'rows': 2,
                                           'style': 'background-color: #d0e2bc'})
        }

    def clean_text(self):
        if self.cleaned_data['hidden_text'] != None:
            text = self.cleaned_data['hidden_text']+self.cleaned_data['text']
            return text
        return self.cleaned_data['hidden_text']
