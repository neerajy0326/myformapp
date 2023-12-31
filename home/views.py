from django.shortcuts import render , HttpResponse ,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.views import LogoutView
from .forms import EditProfileForm
from .forms import UserRegistrationForm 
from .models import CustomUser,Comment
from .forms import PinSetupForm
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import BlogPost ,WalletTransaction
from .models import DiceRollGame
import random
from .models import Coupon
from .forms import BlogPostForm,CommentForm , ChatMessageForm
import os
from django.db.models import Q
from django.utils import timezone
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
from datetime import timedelta
from .models import VerificationPlan, VerificationBadge
from decimal import Decimal
from django.http import JsonResponse
import time
from .models import CustomUser, UserConnection ,Notification , ChatMessage
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore





@login_required
def chat(request):
    if request.user.is_authenticated:
           if request.user.show_active_status:
            request.user.last_active = timezone.now()
            request.user.save()
    users = CustomUser.objects.exclude(pk=request.user.pk)  
    return render(request, "chat.html", {'users': users})

def chat_with_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)  
    chats = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
    ).order_by('timestamp')
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.sender = request.user
            chat.receiver = user
            
            chat.save()

            
    else:
        form = ChatMessageForm()

    unread_messages = chats.filter(receiver=request.user, is_read=False)
    unread_messages.update(is_read=True)    
        
    return render(request, 'chat_page.html', {'user': user  , 'chats' : chats , 'form': form})

def delete_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id, sender=request.user)
    message.delete()
    return HttpResponse(status=204)




def users(request):
    
    users = CustomUser.objects.exclude(id=request.user.id)
    unread_conversations_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).values('sender').distinct().count()
  
    user_actions = {}

    for user in users:
        try:
            latest_message = ChatMessage.objects.filter(
                Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
            ).latest('timestamp')

            if latest_message.sender == request.user:
                user_actions[user.id] = {'action': 'sent', 'timestamp': latest_message.timestamp}
            elif not latest_message.is_read:
            # Check if user.id is in the dictionary before accessing it
              if user.id not in user_actions:
                user_actions[user.id] = {'action': 'unread', 'unread_count': 1, 'timestamp': latest_message.timestamp}
              else:
                # Check and increment the unread count
                unread_count = user_actions[user.id].get('unread_count', 0)
                user_actions[user.id] = {'action': 'unread', 'unread_count': unread_count + 1, 'timestamp': latest_message.timestamp}
            else:
                user_actions[user.id] = {'action': None}
        except ChatMessage.DoesNotExist:
            user_actions[user.id] = {'action': None}

    context = {
        'users': users,
        'user_actions': user_actions,
        'unread_conversations_count': unread_conversations_count
    }

    return render(request, 'users.html', context)


@login_required
def follow_user(request,pk):
    user_to_follow = get_object_or_404(CustomUser, pk=pk)
    connection, created = UserConnection.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    if created:
        user_to_follow.followers_count += 1
        user_to_follow.save()
        request.user.following_count += 1
        request.user.save()

        Notification.objects.create(
            user=user_to_follow,
            source_user=request.user,
            notification_type='follow'
        )


    referer = request.META.get('HTTP_REFERER', '')
    print("Referer:", referer)

    
    
    if 'user_detail' in referer:
        return redirect('user_detail', pk=pk)
    else:
        return redirect('user_list')

@login_required
def unfollow_user(request, pk):
    user_to_unfollow = get_object_or_404(CustomUser, pk=pk)
    try:
        connection = UserConnection.objects.get(
            follower=request.user,
            following=user_to_unfollow
        )
        connection.delete()
        user_to_unfollow.followers_count -= 1
        user_to_unfollow.save()
        request.user.following_count -= 1
        request.user.save()
    except UserConnection.DoesNotExist:
        pass

    referer = request.META.get('HTTP_REFERER', '')


    if 'user_detail' in referer:
        return redirect('user_detail', pk=pk)
    else:
        return redirect('user_list')

@login_required
def user_followers(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    followers = UserConnection.objects.filter(following=user)
    return render(request, 'user_followers.html', {'user': user, 'followers': followers})

@login_required
def user_following(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    following = UserConnection.objects.filter(follower=user)
    return render(request, 'user_following.html', {'user': user, 'following': following})








@login_required
def delete_account(request):
    if request.method == 'POST':
         user = request.user
         user.delete()
         logout(request)  
         return redirect('login_page')  
   

    return render(request, 'delete_account.html')


def logout_view(request):
    logout(request) 
    return redirect('login_page')

def index(request):
    if request.user.is_authenticated:
        return redirect('blog_list') 
    return render(request,"index.html")

def about(request):
    if request.user.is_authenticated:
        return redirect('blog_list') 
    return render(request,"about.html")

def services(request):
    if request.user.is_authenticated:
        return redirect('blog_list') 
    return render(request,"services.html")

def contact(request):
    if request.user.is_authenticated:
        return redirect('blog_list') 
    return render(request,"contact.html")  

def login_page(request): 
    if request.user.is_authenticated:
        return redirect('blog_list')   
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        

        user = authenticate(request, email=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('/blog_list')
        
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login_page.html')

def account_settings(request):
    return render(request, 'account_settings.html')

@login_required
def change_password(request):
    if request.user.show_active_status:
            request.user.last_active = timezone.now()
            request.user.save()
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password has been successfully updated.')
            return redirect('profile')  # Redirect to the profile page after password change
        else:
            messages.error(request, 'Please use strong password')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import EditProfileForm
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

@login_required
def edit_profile(request):
    request.user.last_active = timezone.now()
    request.user.save()
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            remove_profile_picture = request.POST.get('remove_profile_picture', False)

            if remove_profile_picture == 'on':
                if user.profile_picture:
                    try:
                        default_storage.delete(user.profile_picture.name)
                    except:
                        pass
             
                user.profile_picture.delete()
                user.profile_picture = None
                user.save()

                messages.success(request, 'Your profile picture has been removed.')
            else:
                form.save()
                messages.success(request, 'Your profile has been updated.')
                
            return redirect('profile') 
        else:
            messages.error(request, 'Contact number is required before saving')

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
           
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(str(user.pk))) 
            
            ngrok_url = settings.NGROK_URL
           
            
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
    unread_conversations_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).values('sender').distinct().count()

    if request.user.show_active_status:
        request.user.last_active = timezone.now()
        request.user.save()

    user = request.user.username
    my_blogs_count = BlogPost.objects.filter(author=user).count()
    unread_notifications = Notification.objects.filter(user=request.user, seen=False).count()

    return render(request, 'profile.html', {'my_blogs_count': my_blogs_count, 'unread_count': unread_notifications ,'unread_conversations_count' : unread_conversations_count})
   

def register(request):
    if request.user.is_authenticated:
        return redirect('blog_list') 
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
            user.set_password(password)  

            user.save()
            messages.success(request, 'Account has been successfully created for user ' + full_name)
            return redirect('login_page')
        else:
            
            messages.error(request, 'Username not available. Choose different one!')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def blog_list(request):
    unread_conversations_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).values('sender').distinct().count()

    
    request.user.last_active = timezone.now()
    request.user.save()
    
    following_usernames = UserConnection.objects.filter(follower=request.user).values_list('following__username', flat=True)
    posts = BlogPost.objects.filter(Q(author__in=following_usernames) | Q(author=request.user.username)).order_by('-pub_date')
    return render(request, 'blog_list.html', {'posts': posts , 'unread_conversations_count':unread_conversations_count})


@login_required
def blog_detail(request, pk):
    unread_conversations_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).values('sender').distinct().count()

    request.user.last_active = timezone.now()
    request.user.save()
    blog_post = get_object_or_404(BlogPost, pk=pk)
    comments = blog_post.comments.all() 

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = blog_post
            comment.author = request.user
            comment.save()

            if request.user.username != blog_post.author:
       
                author_user = CustomUser.objects.get(username=blog_post.author)
        
       
                Notification.objects.create(
                    user=author_user,  
                    notification_type='comment',
                    source_user=request.user,
                    blog_post=blog_post,
                    comment=comment 
                )
            
            return redirect('blog_detail', pk=blog_post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog_detail.html', {'blog_post': blog_post, 'comments': comments, 'form': form ,'unread_conversations_count':unread_conversations_count})




def delete_comment(request, post_pk, comment_id):
    request.user.last_active = timezone.now()
    request.user.save()
    if request.method == 'POST':
        
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
           
            pass
        else:
            
            if request.user == comment.author or request.user == comment.post.author:
                comment.delete()
    return redirect('blog_detail', pk=post_pk)

@login_required
def blog_create(request):
    unread_conversations_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).values('sender').distinct().count()

    
    request.user.last_active = timezone.now()
    request.user.save()
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)  
            blog_post.author = request.user.username
            blog_post.save() 
            award_wallet_money_for_posts(request.user.username, 4, 50 , request)
            coupon_code = "1234" 
            award_coupon_for_posts(request.user.username, coupon_code, request)
            messages.success(request, 'Blog post created successfully.')
            return redirect('blog_list')  
           
        else:
            messages.error(request, 'There was an error. Please correct the form and try again.')
    else:
        form = BlogPostForm()
    return render(request, 'blog_form.html', {'form': form , 'unread_conversations_count':unread_conversations_count})


@login_required
def blog_update(request, pk):
    request.user.last_active = timezone.now()
    request.user.save()
   
    blog_post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST,request.FILES, instance=blog_post)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm(instance=blog_post)
    return render(request, 'blog_form.html', {'form': form})



@login_required
def blog_delete(request, pk):
    request.user.last_active = timezone.now()
    request.user.save()
   
    blog_post = get_object_or_404(BlogPost, pk=pk)
    if blog_post.author == request.user.username:
     if request.method == 'POST':
        if blog_post.media:
                 blog_post.media.delete()
      
        blog_post.delete()

        return redirect('blog_list')
    return render(request, 'blog_confirm_delete.html', {'blog_post': blog_post})


@login_required
def my_blogs(request):
    unread_conversations_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).values('sender').distinct().count()

    if request.user.show_active_status:
            request.user.last_active = timezone.now()
            request.user.save()
    current_user = request.user.username  
    my_blogs = BlogPost.objects.filter(author=current_user).order_by('-pub_date')
    my_blogs_count = my_blogs.count()
    return render(request, 'my_blogs.html', {'my_blogs': my_blogs, 'my_blogs_count': my_blogs_count ,'unread_conversations_count':unread_conversations_count})


@login_required
def user_list(request):
    unread_conversations_count = ChatMessage.objects.filter(receiver=request.user, is_read=False).values('sender').distinct().count()

    
    if request.user.show_active_status:
            request.user.last_active = timezone.now()
            request.user.save()
    users = CustomUser.objects.all()

    following_users = UserConnection.objects.filter(follower=request.user).values_list('following__id', flat=True)

    return render(request, 'user_list.html', {'users': users , 'following_users': following_users,'unread_conversations_count':unread_conversations_count})

def user_detail(request, pk):
    request.user.last_active = timezone.now()
    request.user.save()
    
    user = get_object_or_404(CustomUser, pk=pk)
    user_blogs_count = BlogPost.objects.filter(author=user.username).count()
    user_blogs = BlogPost.objects.filter(author=user.username).order_by('-pub_date')
    followers = UserConnection.objects.filter(following=user)
    is_following = UserConnection.objects.filter(
        follower=request.user,
        following=user
    ).exists()
  
    return render(request, 'user_detail.html', {'user': user ,'user_blogs_count': user_blogs_count, 'user_blogs': user_blogs ,'is_following': is_following ,'followers': followers}  )


@login_required
def like_post(request, pk):
    request.user.last_active = timezone.now()
    request.user.save()
    blog_post = get_object_or_404(BlogPost, pk=pk)
    is_liked = request.user in blog_post.likes_users.all()

    if is_liked:
        blog_post.likes_users.remove(request.user)
        remove_notification = True
    else:
        blog_post.likes_users.add(request.user)
        remove_notification = False
    blog_post.save()

    if remove_notification:
        author_user = CustomUser.objects.get(username=blog_post.author)
        Notification.objects.filter(
            user=author_user,
            notification_type='like',
            source_user=request.user,
            blog_post=blog_post
        ).delete()
    if not is_liked and request.user.username != blog_post.author:
       
        author_user = CustomUser.objects.get(username=blog_post.author)
        
       
        Notification.objects.create(
            user=author_user,  
            notification_type='like',
            source_user=request.user,
            blog_post=blog_post
        )
    return redirect('blog_detail', pk=pk)


def badge_selection(request):
    request.user.last_active = timezone.now()
    request.user.save()
    plans = VerificationPlan.objects.all()
    return render(request, 'badge_selection.html', {'plans': plans})

def payment(request, plan_id):
    user = request.user
    owned_coupon_codes = user.owned_coupons.split(",") if user.owned_coupons else []
    
    if not user.pin:
        messages.warning(request, 'Please set up a PIN first.')
        return redirect('setup_pin')
    plan = VerificationPlan.objects.get(pk=plan_id)
    coupons = Coupon.objects.all()
    original_price = plan.price
    updated_price = request.session.get('updated_price', original_price)

    if request.method == 'POST':
        if 'apply_coupon' in request.POST:  
            coupon_code = request.POST.get('coupon_code')

            try:
                coupon = Coupon.objects.get(code=coupon_code)
                updated_price = original_price * (100 - coupon.discount_percent) / 100
                request.session['updated_price'] = float(updated_price)
                messages.success(request, f'{coupon.discount_percent}% Discount coupon applied successfully!')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code.')

        elif 'remove_coupon' in request.POST: 
             updated_price = original_price 
             request.session['updated_price'] = float(updated_price)      

        elif 'pay_now' in request.POST:  
            pin = request.POST.get('pin')
            

        
            if user.pin == pin:
               if user.balance >= updated_price:
                  
                  expiration_date = timezone.now() + timedelta(hours=plan.duration_days)
                  updated_price_decimal = Decimal(request.session.get('updated_price', str(original_price)))
                  request.user.balance -= updated_price_decimal
                  request.user.verified_badge = True
                  request.user.verification_expiration = expiration_date
                  request.user.save()

                  WalletTransaction.objects.create(
                  sender=request.user,
                  receiver=request.user, 
                  amount=updated_price_decimal,
                  description=f'Payment for Verification Badge'
                  )
                  VerificationBadge.objects.create(user=user, plan=plan, verified=True , verification_expiration=expiration_date)
                  send_verification_success_email(user, plan)
                  messages.success(request, 'Payment successful. You are now verified!')
                  if 'updated_price' in request.session:
                        del request.session['updated_price']
                  return redirect('profile')  
               else:
                  messages.error(request, 'Insufficient wallet balance.')
            else:
                messages.error(request, 'Incorrect PIN. Payment not processed.')
    if user.verification_expiration and user.verification_expiration <= timezone.now():
        user.verified_badge = False
        user.save()            

    return render(request, 'payment.html', {'plan': plan, 'coupons': coupons, 'updated_price': updated_price, 'owned_coupon_codes': owned_coupon_codes})

def send_verification_success_email(user ,plan):
    subject = 'Verification Badge Success'
    
    html_message = render_to_string('verification_success_email.html',  {'user': user, 'plan': plan})

    from_email = f'MyForm <{settings.EMAIL_HOST_USER}>'

    send_mail(
        subject,
        '', 
        from_email,
        [user.email],
        
        html_message=html_message,
    )



@login_required
def cancel_verification(request):
  request.user.last_active = timezone.now()
  request.user.save()
  if request.method == 'POST':  
     if request.user.is_authenticated:
         user = request.user
         user.verified_badge = False
         user.save()

         try:
             verification_badge = VerificationBadge.objects.get(user=user)
             verification_badge.delete()  
         except VerificationBadge.DoesNotExist:
             pass  
     send_badgecancel_email(request.user)
     return redirect('profile')
  
  return render(request, 'cancel_verification.html')

def send_badgecancel_email(user):
    subject = 'Verification Badge Cancelled'
    
    html_message = render_to_string('badgecancel_email.html',  {'user': user})

    from_email = f'MyForm <{settings.EMAIL_HOST_USER}>'

    send_mail(
        subject,
        '', 
        from_email,
        [user.email],
        
        html_message=html_message,
    )

   
def transfer_money(request):
    request.user.last_active = timezone.now()
    request.user.save()
    user = request.user
    
    if not user.pin:
        messages.warning(request, 'Please set up a PIN first.')
        return redirect('setup_pin')
    if request.method == 'POST':
        sender = request.user
        receiver_username = request.POST.get('receiver_username')
        amount = Decimal(request.POST.get('amount'))
        entered_pin = request.POST.get('pin')

        try:
            receiver = CustomUser.objects.get(username=receiver_username)
        except CustomUser.DoesNotExist:
            return render(request, 'transfer_money.html', {'error_message': 'No user with this username'})
        
        if sender == receiver:
            return render(request, 'transfer_money.html', {'error_message': 'You cannot send money to yourself.'})
        if amount > 0:
            
         if sender.pin == entered_pin:
           if sender.balance >= amount:
              sender.balance -= amount
              receiver.balance += amount
              sender.save()
              receiver.save()

              WalletTransaction.objects.create(sender=sender, receiver=receiver, amount=amount,timestamp=timezone.now())
              messages.success(request, f'Successfully transferred Rs {amount} to {receiver.username}.')
              return redirect('profile')
           else:
               return render(request, 'transfer_money.html', {'error_message': 'Insufficient balance.'})
         else:
              return render(request, 'transfer_money.html', {'error_message': 'Incorrect PIN.'})  
        else:
             return render(request, 'transfer_money.html', {'error_message': 'Enter an valid amount'})
    return render(request, 'transfer_money.html')  


def wallet_detail(request):
    request.user.last_active = timezone.now()
    request.user.save()
    user = request.user
    transactions = WalletTransaction.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-timestamp')[:10]
    
    context = {
        'user': user,
        'transactions': transactions,
    }
    
    return render(request, 'wallet_detail.html', context)


def setup_pin(request):
    request.user.last_active = timezone.now()
    request.user.save()
    if request.method == 'POST':
        form = PinSetupForm(request.POST)
        if form.is_valid():
            pin = form.cleaned_data['pin']
            confirm_pin = form.cleaned_data['confirm_pin']
            if pin == confirm_pin:
                
                request.user.pin = pin
                request.user.save()
                messages.success(request, 'PIN set successfully.')
                return redirect('wallet_detail')
            else:
                return render(request, 'pin_setup.html', {'error_message': 'PIN does not match!'})

    else:
        form = PinSetupForm()

    return render(request, 'pin_setup.html', {'form': form})




def add_funds(request):
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        max_allowed_amount = Decimal(1000)
        
        if amount > 0 and amount <= max_allowed_amount:
            user = request.user
            user.balance += amount
            user.save()
            messages.success(request, f'Successfully added Rs {amount} to your wallet.')
            return redirect('profile')
        elif amount <= 0:
            messages.error(request, 'Enter a valid positive amount.')
        else:
            messages.error(request, f'Amount exceeds the maximum limit of Rs {max_allowed_amount}.')
    return render(request, 'add_funds.html')





def change_pin(request):
    if request.method == 'POST':
        current_pin = request.POST.get('current_pin')
        new_pin = request.POST.get('new_pin')
        confirm_new_pin = request.POST.get('confirm_new_pin')
        user = request.user

        if user.pin == current_pin:
            if new_pin == confirm_new_pin:
                user.pin = new_pin
                user.save()
                messages.success(request, 'PIN changed successfully.')
                return redirect('profile')
            else:
                messages.error(request, 'New PINs do not match.')
        else:
            messages.error(request, 'Incorrect current PIN.')
    return render(request, 'change_pin.html')


@login_required
def view_notifications(request):
    request.user.last_active = timezone.now()
    
    if request.path == reverse('notifications'): 
        request.user.last_seen_notification = timezone.now()
        request.user.save()

        
        Notification.objects.filter(user=request.user, seen=False).update(seen=True)

    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return redirect('notifications')


def under_construction(request):
    return render(request,'uc.html')



@login_required
def dice_roll_game(request):
    if request.method == 'POST':
        bet_amount = Decimal(request.POST['bet_amount'])
        chosen_number = int(request.POST['chosen_number'])
        
        if bet_amount <= 0:
            return render(request, 'dice_roll_game.html', {'error': 'Bet amount must be positive.'})
        
        if bet_amount < 10:
            return render(request, 'dice_roll_game.html', {'error': 'Minimum amount should be Rs 10'})
        
        if bet_amount > request.user.balance:
            return render(request, 'dice_roll_game.html', {'error': 'Insufficient balance.'})
        
        rolled_number = random.randint(1, 6)  
        won = rolled_number == chosen_number
        
        if won:
            reward = bet_amount
            request.user.balance += reward*4
        else:
            request.user.balance -= bet_amount
        
        request.user.save()
        
        DiceRollGame.objects.create(
            user=request.user,
            bet_amount=bet_amount,
            chosen_number=chosen_number,
            rolled_number=rolled_number,
            won=won
        )
        game_result = "You won!" if won else "You lost!"
        return render(request, 'dice_roll_game.html', {'game_result': game_result , 'rolled_number': rolled_number})
    
    return render(request, 'dice_roll_game.html')

@login_required
def game_history(request):
    game_history = DiceRollGame.objects.filter(user=request.user).order_by('-timestamp')
    for game in game_history:
        game.won_amount = game.bet_amount*4
    return render(request, 'game_history.html', {'game_history': game_history})




def clear_all_games(request):
    game_history = DiceRollGame.objects.filter(user=request.user)
    
    if game_history.exists():
        game_history.delete()
        messages.success(request, 'All game history cleared successfully.')
    else:
        messages.info(request, 'No game history to clear.')

    return redirect('game_history')



def award_coupon_for_posts(username, coupon_code, request):
    try:
        user = CustomUser.objects.get(username=username)
        today = timezone.now().date()
        posts_today = BlogPost.objects.filter(author=username, timestamp__date=today).count()

        if posts_today == 2 and not request.session.get('coupon_awarded'):
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                user.owned_coupons += ("," + coupon_code)
                request.session['coupon_awarded'] = True 
                messages.success(request, 'Congratulations! You have received a coupon for making two posts today.Use at payment page')
                
                user.save()
            except Coupon.DoesNotExist:
                pass
    except CustomUser.DoesNotExist:
        pass




def award_wallet_money_for_posts(username, post_count, reward_amount , request):
    try:
        user = CustomUser.objects.get(username=username)
        today = timezone.now().date()
        posts_today = BlogPost.objects.filter(author=username, pub_date__date=today).count()

        if posts_today >= post_count and not request.session.get('wallet_rewarded'):
            user.balance += reward_amount
            request.session['wallet_rewarded'] = True
            user.save()

            messages.success(request, f'You have been awarded Rs {reward_amount}  for posting {post_count} posts today!')
    except CustomUser.DoesNotExist:
        pass    