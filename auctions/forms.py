from django import forms

from .models import Auction ,Comment,    Bid


class auctions_new(forms.ModelForm):
    # protected $table = 'auctions_new';

    class Meta:
        model  = Auction
        fields = ['title', 'desc',
                  'min_value', 'image', 'category', 'author' , 'date_added']
        exclude = [ 'winner']


class CommentForm(forms.ModelForm):
    class Meta:
        model= Comment
        fields = ['comments']

    comments = forms.CharField(label="", widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Comment here !',
            'rows': 4,
            'cols': 50
        }))

class Activeform(forms.ModelForm):
    class Meta:
        model =Auction
        fields =['is_active']
        active_choice = (
            ("active", "active"),
            ("not active", "not active"),
        )
        Close= forms.ChoiceField(choices= active_choice)