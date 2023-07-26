from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin 
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


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
    is_staff = models.BooleanField(default=False)  # Add the is_staff attribute
    is_superuser = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.CharField(max_length=200, blank=True, null=True)

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'contact_number','username']

    objects = CustomUserManager()  # Use the custom manager for the objects field

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
    
    
class BlogPost(models.Model):
          title = models.CharField(max_length=100)
          content = models.TextField()
          pub_date = models.DateTimeField(auto_now_add=True)
          author = models.CharField(max_length=100) 
          photo = models.ImageField(upload_to='blog_photos/', blank=True, null=True) 
          likes_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts')         
          
          @property
          def like_count(self):
           return self.likes_users.count()
          
          def __str__(self):
            return self.title 

User = get_user_model()
class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)