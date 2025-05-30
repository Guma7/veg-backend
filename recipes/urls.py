from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet)

urlpatterns = [
    # Rotas específicas devem vir ANTES do router para evitar conflitos
    path('recipes/featured/', views.featured_recipes, name='featured_recipes'),
    path('recipes/search/', views.search_recipes, name='search_recipes'),
    path('recipes/genres/suggest/', views.suggest_tags, name='suggest_tags'),
    path('recipes/categories/', views.get_categories, name='get_categories'),
    path('recipes/<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
    path('recipes/<int:recipe_id>/ratings/', views.get_recipe_ratings, name='get_recipe_ratings'),
    path('recipes/user/<int:user_id>/', views.user_recipes, name='user_recipes'),
    path('recipes/by-slug/<slug:slug>/', views.recipe_by_slug, name='recipe_by_slug'),
    # Router deve vir por último para não capturar as rotas específicas
    path('', include(router.urls)),
]