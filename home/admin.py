from django.contrib import admin
from home.models import CustomUser
from home.models import BlogPost ,Comment

admin.site.register(CustomUser)
admin.site.register(BlogPost)
admin.site.register(Comment)
