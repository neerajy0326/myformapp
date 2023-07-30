from django.shortcuts import render , HttpResponse ,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.views import LogoutView
from .forms import EditProfileForm
from .forms import UserRegistrationForm 
from .models import CustomUser,Comment
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import BlogPost
from .forms import BlogPostForm,CommentForm
import os

from django.contrib.auth.models import User
import requests
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.forms import SetPasswordForm


def chat(request):
    return render(request,"chat.html")

@login_required
def delete_account(request):
    if request.method == 'POST':
         user = request.user
         user.delete()
         logout(request)  # Log the user out after deleting their account
         return redirect('login_page')  
   

    return render(request, 'delete_account.html')


def logout_view(request):
    logout(request) 
    return redirect('login_page')

def index(request):
    return render(request,"index.html")

def about(request):
    return render(request,"about.html")

def services(request):
    return render(request,"services.html")

def contact(request):
    return render(request,"contact.html")  

def login_page(request):  
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        

        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('/profile')
        
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login_page.html')

def account_settings(request):
    return render(request, 'account_settings.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password has been successfully updated.')
            return redirect('profile')  # Redirect to the profile page after password change
        else:
            messages.error(request, 'Please correct the error(s) below.')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import EditProfileForm
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            remove_profile_picture = request.POST.get('remove_profile_picture', False)

            if remove_profile_picture == 'on':
                # Remove the profile picture from the database and clear the profile_picture field
                user.profile_picture.delete()
                user.profile_picture = None
                user.save()

                messages.success(request, 'Your profile picture has been removed.')
            else:
                form.save()
                messages.success(request, 'Your profile has been updated.')
                
            return redirect('profile')  # Redirect to the profile page after profile edit
        else:
            messages.error(request, 'Username already exists ! Choose different ')

    else:
        form = EditProfileForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form})
from django.http import HttpResponse 
def reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            user = None

        if user:
            # Generate the password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(str(user.pk))) 
            
            ngrok_url = settings.NGROK_URL
            # Build the reset link
            
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            reset_link = f'{ngrok_url}{reset_url}'

            # Send the password reset email
            subject = 'Password Reset Request'
            from_email = f'MyForm <{settings.EMAIL_HOST_USER}>'
            html_message = render_to_string('reset_password_email.html', {
                'user': user,
                'reset_link': reset_link,
            })
            send_mail(subject,'', from_email, [email] ,html_message=html_message)

            messages.success(request, 'An email has been sent with instructions to reset your password.')
        else:
            messages.error(request, 'User with this email address does not exist.')

        return redirect('reset')

    return render(request, 'reset.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset. You can now log in with your new password.')
                return redirect('login_page')
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})

    messages.error(request, 'Invalid reset link. Please try again.')
    return redirect('login_page')

@login_required
def profile(request):
    user = request.user.username
    my_blogs_count = BlogPost.objects.filter(author=user).count()
    return render(request, 'profile.html', {'my_blogs_count': my_blogs_count})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if get_user_model().objects.filter(email=email).exists():
                messages.error(request, 'User with this email address already exists.')
                return redirect('register')

            full_name = form.cleaned_data['full_name']
            contact_number = form.cleaned_data['contact_number']
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            user = get_user_model().objects.create_user(email=email, contact_number=contact_number, full_name=full_name,username=username)
            user.set_password(password)  # Set the password properly

            user.save()
            messages.success(request, 'Account has been successfully created for user ' + full_name)
            return redirect('login_page')
        else:
            
            return HttpResponse("Form is invalid.")
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def blog_list(request):
    # Read operation - Fetch all blog posts from the database
    blog_posts = BlogPost.objects.all().order_by('-pub_date')
    return render(request, 'blog_list.html', {'blog_posts': blog_posts})
@login_required
def blog_detail(request, pk):
    
    blog_post = get_object_or_404(BlogPost, pk=pk)
    comments = blog_post.comments.all()  # Get all comments associated with the post

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = blog_post
            comment.author = request.user
            comment.save()
            return redirect('blog_detail', pk=blog_post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog_detail.html', {'blog_post': blog_post, 'comments': comments, 'form': form})




def delete_comment(request, post_pk, comment_id):
    if request.method == 'POST':
        # Fetch the comment by comment_id
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            # Handle the case if the comment doesn't exist
            # You can redirect or show an error message here
            pass
        else:
            # Check if the current user is the author of the comment or the blog post
            if request.user == comment.author or request.user == comment.post.author:
                comment.delete()
    return redirect('blog_detail', pk=post_pk)

@login_required
def blog_create(request):
    # Create operation - Save a new blog post to the database
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)  
            blog_post.author = request.user.username
            blog_post.save() 
            messages.success(request, 'Blog post created successfully.')
            return redirect('blog_list')  
           
        else:
            messages.error(request, 'There was an error. Please correct the form and try again.')
    else:
        form = BlogPostForm()
    return render(request, 'blog_form.html', {'form': form})


@login_required
def blog_update(request, pk):
    # Update operation - Update an existing blog post in the database
    blog_post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=blog_post)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm(instance=blog_post)
    return render(request, 'blog_form.html', {'form': form})



@login_required
def blog_delete(request, pk):
    # Delete operation - Delete a blog post from the database
    blog_post = get_object_or_404(BlogPost, pk=pk)
    if blog_post.author == request.user.username:
     if request.method == 'POST':
        if blog_post.photo:
                
                

               
              

                
                blog_post.photo.delete()

           
        blog_post.delete()

        return redirect('blog_list')
    return render(request, 'blog_confirm_delete.html', {'blog_post': blog_post})


@login_required
def my_blogs(request):
    current_user = request.user.username  
    my_blogs = BlogPost.objects.filter(author=current_user).order_by('-pub_date')
    my_blogs_count = my_blogs.count()
    return render(request, 'my_blogs.html', {'my_blogs': my_blogs, 'my_blogs_count': my_blogs_count})


@login_required
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})

def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user_blogs_count = BlogPost.objects.filter(author=user.username).count()
    user_blogs = BlogPost.objects.filter(author=user.username).order_by('-pub_date')
  
    return render(request, 'user_detail.html', {'user': user ,'user_blogs_count': user_blogs_count, 'user_blogs': user_blogs}  )


@login_required
def like_post(request, pk):
    blog_post = get_object_or_404(BlogPost, pk=pk)
    if request.user in blog_post.likes_users.all():
        blog_post.likes_users.remove(request.user)
    else:
        blog_post.likes_users.add(request.user)
    blog_post.save()
    return redirect('blog_detail', pk=pk)
