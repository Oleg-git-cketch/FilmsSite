from django.contrib import admin
from .models import Category, Film, Comments, User

# Register your models here.
admin.site.register(Category)
admin.site.register(Film)
admin.site.register(Comments)
admin.site.register(User)