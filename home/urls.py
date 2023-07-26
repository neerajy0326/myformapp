from django.contrib import admin
from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('' , views.login_page , name="home"),
    path('about',views.about,name="about"),
    path('home',views.index,name="home" ),
    path('services',views.services , name="services"),
    path('contact',views.contact, name="contact"),
    path('login_page',views.login_page ,name="login_page"),
    path('reset',views.reset ,name="reset"),
    path('register',views.register ,name="register"),
    path('profile', views.profile, name='profile'),
    path('logout', views.logout_view, name='logout'),
    path('profile/password_change/', views.change_password, name='change_password'),
    path('profile/edit_profile/', views.edit_profile, name='edit_profile'),
    path('profile/blog_list', views.blog_list, name='blog_list'),
    path('profile/blog_list/post/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('profile/blog_list/post/<int:pk>/like/', views.like_post, name='like_post'),
    path('profile/blog_list/create/', views.blog_create, name='blog_create'),
    path('profile/blog_list/update/<int:pk>/', views.blog_update, name='blog_update'),
    path('profile/blog_list/delete/<int:pk>/', views.blog_delete, name='blog_delete'),
    path('profile/blog_list/my_blogs/', views.my_blogs, name='my_blogs'),
    path('profile/edit_profile/delete_account/', views.delete_account, name='delete_account'),
    path('profile/user_list/',views.user_list, name='user_list'),
    path('profile/user_list/user_detail/<int:pk>/', views.user_detail, name='user_detail'),
    path('profile/news_list/',views.news_list, name='news_list'),
    path('profile/account_settings/', views.account_settings, name='account_settings'),
    path('profile/blog_list/post/<int:post_pk>/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)