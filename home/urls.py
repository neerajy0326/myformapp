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
    path('blog_list', views.blog_list, name='blog_list'),
    path('blog_list/post/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('blog_list/post/<int:pk>/like/', views.like_post, name='like_post'),
    path('blog_list/create/', views.blog_create, name='blog_create'),
    path('blog_list/update/<int:pk>/', views.blog_update, name='blog_update'),
    path('blog_list/delete/<int:pk>/', views.blog_delete, name='blog_delete'),
    path('blog_list/my_blogs/', views.my_blogs, name='my_blogs'),
    path('profile/edit_profile/delete_account/', views.delete_account, name='delete_account'),
    path('user_list/',views.user_list, name='user_list'),
    path('user_detail/<int:pk>/', views.user_detail, name='user_detail'),
    path('chat/',views.chat, name='chat'),
    path('profile/account_settings/', views.account_settings, name='account_settings'),
    path('blog_list/post/<int:post_pk>/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('reset/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('profile/badge_selection/', views.badge_selection, name='badge_selection'),
    path('profile/payment/<int:plan_id>/', views.payment, name='payment'),
    path('profile/transfer_money/', views.transfer_money, name='transfer_money'),
    path('profile/account_settings/cancel_verification', views.cancel_verification, name='cancel_verification'),
    path('profile/wallet_detail/', views.wallet_detail, name='wallet_detail'),
    path('profile/setup_pin/', views.setup_pin, name='setup_pin'),
    path('profile/under_construction', views.under_construction, name='under_construction'),
    path('profile/wallet_detail/add_funds/', views.add_funds, name='add_funds'),
    path('profile/change_pin/', views.change_pin, name='change_pin'),
    path('profile/user_detail/<int:pk>/follow/', views.follow_user, name='follow_user'),
    path('profile/user_detail/<int:pk>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('profile/user_detail/<int:pk>/followers/', views.user_followers, name='user_followers'),
    path('profile/user_detail/<int:pk>/following/', views.user_following, name='user_following'),
    path('notifications/', views.view_notifications, name='notifications'),
    path('clear_notifications/', views.clear_notifications, name='clear_notifications'),
    path('dice_roll_game/', views.dice_roll_game, name='dice_roll_game'),
    path('game_history/', views.game_history, name='game_history'),

    
  
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)