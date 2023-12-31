from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser ,BlogPost ,Comment , ChatMessage

class UserRegistrationForm(forms.ModelForm):
   
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    contact_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
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
        fields = ['full_name', 'contact_number', 'date_of_birth', 'profile_picture' ,'bio','show_active_status']

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'media']

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        media = cleaned_data.get('media')

        if not content and not media:
            raise forms.ValidationError("Please choose at least one option between Content and Photo.")
        
        return cleaned_data
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class PinSetupForm(forms.Form):
    pin = forms.CharField(max_length=4, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_pin = forms.CharField(max_length=4, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage    
        fields = ['content']