from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('feed/', views.feed, name='feed'),
    path('logout/', views.logout_view, name='logout'),

    path('like/<int:post_id>/', views.like_post, name='like'),
    path('comment/<int:post_id>/', views.comment_post, name='comment'),

    path('profile/<str:username>/', views.profile, name='profile'),
    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('notifications/', views.notifications, name='notifications'),
    path('request/<int:request_id>/<str:action>/', views.handle_request),
    path('followers/<str:username>/', views.followers_list),
    path('following/<str:username>/', views.following_list),
    path('search/', views.search, name='search'),
    path('post/new/', views.create_post, name='create_post'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

]
