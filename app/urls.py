from django.urls import path
from .views import home, film, register, login_page, profile, favourite, logout_page, search, comment_page, \
    add_like, change_avatar, comment_reply, change_username, sub_category_page, category_page, confirm_email

urlpatterns = [
    path('', home),
    path('film/<str:pk>/', film),
    path('category/<str:pk>/', category_page),
    path('category/<int:category_id>/sub/<int:sub_category_id>/', sub_category_page),
    path('register/', register),
    path('confirm_email/', confirm_email),
    path('login/', login_page),
    path('logout/', logout_page),
    path('profile/<int:pk>/', profile),
    path('favourite/<int:pk>/', favourite),
    path('search/', search),
    path('comment/add/<int:pk>/', comment_page),
    path('add/like/comment/<int:pk>/', add_like),
    path('change_avatar/', change_avatar),
    path('comment/reply/<int:pk>/', comment_reply),
    path('change_username/', change_username),
]