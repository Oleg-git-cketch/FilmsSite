from django.contrib import admin
from .models import Category, Film, Comments, User, SubCategory
from import_export.admin import ImportExportModelAdmin


@admin.register(Film)
class FilmAdmin(ImportExportModelAdmin):
    pass

# Register your models here.
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Comments)
admin.site.register(User)