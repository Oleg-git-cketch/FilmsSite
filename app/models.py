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
    film_poster = models.ImageField(upload_to='posters', null=True)
    film_description = models.TextField()
    film_rating = models.DecimalField(decimal_places=1, max_digits=2)
    film_date = models.DateField()
    film_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    film_likes = models.IntegerField(default=0)
    film_dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.film_name


class User(AbstractUser):
    user_favourites = models.ManyToManyField(Film, blank=True, related_name='fav_by_users')
    user_avatar = models.ImageField(upload_to='avatars')


class Comments(models.Model):
    comment_film =  models.ForeignKey(Film, on_delete=models.CASCADE)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    comment_text = models.TextField()
    comment_likes = models.IntegerField(default=0)
    comment_dislikes = models.IntegerField(default=0)
    comment_added = models.DateTimeField(auto_now_add=True)

class LikeComment(models.Model):
    like_comment = models.ForeignKey(Comments, on_delete=models.CASCADE)
    like_user = models.ForeignKey(User, on_delete=models.CASCADE)