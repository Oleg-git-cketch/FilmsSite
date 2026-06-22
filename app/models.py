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

class SubCategory(models.Model):
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    sub_category_name = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sub_category_name} - {self.main_category.category_name}'

class Film(models.Model):
    film_name = models.CharField(max_length=128)
    film_search = models.CharField(max_length=128, default='')
    film_slug = models.SlugField(unique=True, blank=True)
    original_name = models.CharField(max_length=128, blank=True)
    director = models.CharField(max_length=32, null=True)
    status = models.CharField(max_length=20, choices=[("released", "Released"), ("coming", "Coming Soon"),], default="released")
    film_video = models.URLField()
    duration = models.PositiveIntegerField(null=True, blank=True, help_text="в минутах")
    film_poster = models.ImageField(upload_to='posters', null=True)
    film_description = models.TextField()
    film_rating = models.DecimalField(decimal_places=1, max_digits=2)
    age_rating = models.CharField(max_length=10, choices=[("0+", "0+"), ("6+", "6+"), ("12+", "12+"), ("16+", "16+"), ("18+", "18+"),], default="16+")
    country = models.CharField(max_length=64, blank=True)
    language = models.CharField(max_length=32, default="en")
    budget =  models.CharField(max_length=64, default=0)
    film_date = models.DateField()
    film_subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    film_likes = models.IntegerField(default=0)
    film_dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.film_name


class User(AbstractUser):
    user_favourites = models.ManyToManyField(Film, blank=True, related_name='fav_by_users')
    user_avatar = models.ImageField(upload_to='avatars')



class Comments(models.Model):
    comment_film = models.ForeignKey(Film, on_delete=models.CASCADE)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    comment_text = models.TextField()
    comment_likes = models.IntegerField(default=0)
    comment_dislikes = models.IntegerField(default=0)
    comment_added = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    def __str__(self):
        return f'{self.comment_film.film_name}, {self.comment_text}'

class LikeComment(models.Model):
    like_comment = models.ForeignKey(Comments, on_delete=models.CASCADE)
    like_user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('like_comment', 'like_user')

    def __str__(self):
        return f"{self.like_user} -> {self.like_comment}"