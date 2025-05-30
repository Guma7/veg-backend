from django.contrib import admin
from .models import Recipe, Rating

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'recipe_class', 'created_at']
    list_filter = ['recipe_class']
    search_fields = ['title', 'ingredients', 'instructions']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user', 'score', 'created_at']
    list_filter = ['score']
