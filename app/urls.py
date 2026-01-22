from django.urls import path
from .views import home, film, category, register, login_page, profile, favourite, logout_page, search

urlpatterns = [
    path('', home),
    path('film/<int:pk>/', film),
    path('category/<str:pk>/', category),
    path('register', register),
    path('login', login_page),
    path('logout', logout_page),
    path('profile', profile),
    path('favourite/<int:pk>/', favourite),
    path('search/', search)
]