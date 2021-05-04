from .models import Comment, Reply
from django import forms

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body', 'notify',)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'col': 3, 'line-height': 1.5, }),
            'notify': forms.CheckboxInput(attrs={'checked': True})
            }
        labels = {'body': False}


class ReplyForm(forms.ModelForm):

    class Meta:
        model = Reply
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3, 'col': 3, 'line-height': 1.5,}),
            }
        labels = {'body': False}