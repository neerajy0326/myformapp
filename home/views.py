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
        print(email)  # Debugging line
        print(password)  # Debugging line

        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('/profile')
        
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login_page.html')

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

def reset(request):
    return render(request,"reset.html")

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
                # Get the file path of the photo
                file_path = blog_post.photo.path

                # Delete the photo from the media files
                if os.path.exists(file_path):
                    os.remove(file_path)

                # Remove the photo from the database
                blog_post.photo.delete()

            # Delete the blog post
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



