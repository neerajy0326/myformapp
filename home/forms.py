from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser ,BlogPost ,Comment

class UserRegistrationForm(forms.ModelForm):
   
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    contact_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = CustomUser
        fields = ['full_name', 'contact_number', 'email', 'password','username']

class ChangePasswordForm(PasswordChangeForm):
      class Meta:
         model = CustomUser
         fields = []

class EditProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    profile_picture = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control custom-file-input'}), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False)
    previous_profile_picture_url = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'contact_number', 'date_of_birth', 'profile_picture' ,'bio']

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'media']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']