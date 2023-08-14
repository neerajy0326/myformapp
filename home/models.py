from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import magic
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email,username, full_name, contact_number, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,username=username, full_name=full_name, contact_number=contact_number)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, full_name, contact_number, password=None):
        user = self.create_user(email, username,full_name, contact_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):

    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message='Username must contain only letters, digits, and underscores.',
        code='invalid_username'
    )
 

 
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[username_validator],
        help_text='Required. 30 characters or fewer. Letters, digits, and underscores only.',
        error_messages={
            'unique': 'A user with that username already exists.',
        }
    )

    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_staff = models.BooleanField(default=False)  # Add the is_staff attribute
    is_superuser = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.CharField(max_length=200, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    show_active_status = models.BooleanField(default=True)
    last_active = models.DateTimeField(blank=True, null=True)
    verified_badge = models.BooleanField(default=False)
    verification_expiration = models.DateTimeField(null=True, blank=True)
    pin = models.CharField(max_length=4, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    last_seen_notification = models.DateTimeField(blank=True, null=True)
      
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'contact_number','username']

    objects = CustomUserManager()  

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.date_joined = timezone.now()
        super().save(*args, **kwargs)
    
    def has_pin(self):
       return self.pin is not None
     

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.email
    
    def update_last_active(self):
        self.last_active = timezone.now()
        self.save()

def validate_media_type(value):
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(value.read())
    if not file_type.startswith('image/') and not file_type.startswith('video/'):
        raise ValidationError('Unsupported file type. Only images or videos are allowed.')    
    
 
    
class BlogPost(models.Model):
          title = models.CharField(max_length=100)
          content = models.TextField( blank=True , null=True)
          pub_date = models.DateTimeField(auto_now_add=True)
          author = models.CharField(max_length=100) 
          media = models.FileField(upload_to='post_media/', blank=True, null=True, validators=[validate_media_type]) 
          likes_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts')         
          
          @property
          def like_count(self):
           return self.likes_users.count()
          
          def __str__(self):
            return f"{self.title} - {self.likes_users.count()} like" 
          
        

User = get_user_model()
class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return f"{self.post.title} - {self.text}"

class VerificationPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class VerificationBadge(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='verification_badge')
    plan = models.ForeignKey(VerificationPlan, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    verification_expiration = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class WalletTransaction(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_transactions', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=200 , default='Regular Transaction')
    

    def __str__(self):
        return f"{self.description} ,users {self.sender.username},{self.receiver.username} of Rs {self.amount}" 


    
class UserConnection(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')


NOTIFICATION_TYPES = [
    ('like', 'Like'),
    ('comment', 'Comment'),
    ('follow', 'Follow'),
]

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    source_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='source_user', on_delete=models.CASCADE)
    blog_post = models.ForeignKey(BlogPost, blank=True, null=True, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    comment = models.ForeignKey(Comment, blank=True, null=True, on_delete=models.CASCADE) 
 
    def __str__(self):
        return self.user
    
class DiceRollGame(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    chosen_number = models.IntegerField()
    rolled_number = models.IntegerField()
    won = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)  


class Coupon(models.Model):
    code = models.CharField(max_length=10, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code      



