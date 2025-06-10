from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from core.validators import validate_image, validate_youtube_link
from django.utils import timezone
from django.utils.text import slugify
import os
from uuid import uuid4
from cloudinary.models import CloudinaryField



# Definir as choices para os campos selecionáveis
RECIPE_CLASS_CHOICES = [
    ('ENTRADA', 'Entrada'),
    ('PRATO_PRINCIPAL', 'Prato Principal'),
    ('SOBREMESA', 'Sobremesa'),
    ('LANCHE', 'Lanche'),
    ('ANIVERSARIO_VEGANO', 'Aniversário Vegano'),
    ('SUCO', 'Suco'),
    ('DRINK', 'Drink'),
    ('VEG_FRIOS', 'Veg Frios'),
    ('VEG_CARNES', 'Veg Carnes'),
]

STYLE_CHOICES = [
    ('GOURMET', 'Gourmet'),
    ('CASEIRA', 'Caseira'),
]

NUTRITIONAL_LEVEL_CHOICES = [
    ('BAIXO', 'Baixo'),
    ('MEDIO', 'Médio'),
    ('ALTO', 'Alto'),
]

class Recipe(models.Model):
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)]
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    genre = models.CharField(max_length=50)
    recipe_class = models.CharField(max_length=50, choices=RECIPE_CLASS_CHOICES)
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='CASEIRA')
    nutritional_level = models.CharField(
        max_length=50, 
        choices=NUTRITIONAL_LEVEL_CHOICES, 
        blank=True, 
        null=True
    )
    does_not_contain = models.CharField(
        max_length=200, 
        blank=True, 
        null=True
    )
    traditional = models.CharField(
        max_length=200, 
        blank=True, 
        null=True
    )
    ingredients = models.TextField()
    instructions = models.TextField()
    youtube_link = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        validators=[validate_youtube_link]
    )
    image = CloudinaryField(
        'image',
        folder='recipe_images',
        transformation={
            'quality': 'auto:eco',
            'fetch_format': 'auto',
            'crop': 'limit',
            'width': 1920,
            'height': 1080
        }
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['recipe_class']),
            models.Index(fields=['style']),
            models.Index(fields=['genre']),
            models.Index(fields=['nutritional_level']),
            models.Index(fields=['traditional']),
        ]

    def __str__(self):
        return self.title

    def average_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return sum(r.score for r in ratings) / len(ratings)

    def total_ratings(self):
        return self.ratings.count()

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])
        
    def save(self, *args, **kwargs):
        # Gerar slug a partir do título se não existir
        if not self.slug:
            self.slug = slugify(self.title)
            
            # Verificar se o slug já existe e adicionar um sufixo se necessário
            original_slug = self.slug
            counter = 1
            while Recipe.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
                
        super().save(*args, **kwargs)

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    created_at = models.DateTimeField(auto_now_add=True)  # Removed default=timezone.now
    
    class Meta:
        unique_together = ['recipe', 'user']

    def __str__(self):
        return f"{self.user.username}'s rating for {self.recipe.title}"

    def clean(self):
        if self.score < 1 or self.score > 10:
            raise ValidationError('A nota deve estar entre 1 e 10')

class RatingHistory(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='history')
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# RecipeTag foi removido conforme as instruções do documento

def recipe_image_path(instance, filename):
    # Obter a extensão do arquivo original
    ext = filename.split('.')[-1]
    # Criar um nome de arquivo baseado no slug da receita
    recipe_slug = instance.recipe.slug
    # Não precisamos mais de um identificador único, pois o slug já é único
    # Retornar o caminho completo usando apenas o slug da receita
    return f'recipe_images/{recipe_slug}.{ext}'

class RecipeImage(models.Model):
    recipe = models.ForeignKey('Recipe', related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField(
        'image',
        folder='recipe_images',
        transformation={
            'quality': 'auto:eco',
            'fetch_format': 'auto',
            'crop': 'limit',
            'width': 1920,
            'height': 1080
        }
    )
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"Imagem da receita {self.recipe.title}"
