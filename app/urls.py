from django.urls import path
from .views import home, film, category, register, login_page, profile, favourite, logout_page, search, comment_page, \
    add_like

urlpatterns = [
    path('', home),
    path('film/<int:pk>/', film),
    path('category/<str:pk>/', category),
    path('register', register),
    path('login', login_page),
    path('logout', logout_page),
    path('profile', profile),
    path('favourite/<int:pk>/', favourite),
    path('search/', search),
    path('comment/add/<int:pk>', comment_page),
    path('add/like/comment/<int:pk>', add_like)
]