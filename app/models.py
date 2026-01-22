from PIL.ImImagePlugin import number
from django.contrib.auth.models import AbstractUser
from django.db import models
from unicodedata import category


# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name

class Film(models.Model):
    film_name = models.CharField(max_length=128)
    film_video = models.URLField()
    film_description = models.TextField()
    film_rating = models.DecimalField(decimal_places=1, max_digits=2)
    film_date = models.DateField()
    film_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.film_name

class User(AbstractUser):
    user_favourites = models.ManyToManyField(Film, blank=True, related_name='fav_by_users')
    user_avatar = models.ImageField(upload_to='avatars')