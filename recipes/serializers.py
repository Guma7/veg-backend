from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe, Rating, RecipeImage
from users.models import UserProfile
from users.serializers import UserSerializer, UserProfileSerializer



class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ('id', 'user', 'score', 'created_at')

class RecipeImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeImage
        fields = ('id', 'image', 'image_url', 'is_primary', 'created_at')
    
    def get_image_url(self, obj):
        if obj.image:
            # Cloudinary já fornece URLs completas
            return str(obj.image.url)
        return None

class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True, required=False, default=0)
    images = RecipeImageSerializer(many=True, read_only=True, required=False)
    image_url = serializers.SerializerMethodField(read_only=True)
    views_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Recipe
        # Campos obrigatórios para cadastro: title, recipe_class, genre, style, ingredients, instructions
        # Campos opcionais: nutritional_level, does_not_contain, traditional, youtube_link, images
        fields = [
            'id', 'title', 'slug', 'recipe_class', 'genre', 'style',
            'ingredients', 'instructions',
            'nutritional_level', 'does_not_contain', 'traditional',
            'youtube_link', 'images', 'author', 'image_url', 'average_rating', 'views_count'
        ]
        extra_kwargs = {
            'title': {'required': True},
            'recipe_class': {'required': True},
            'genre': {'required': True},
            'style': {'required': True},
            'ingredients': {'required': True},
            'instructions': {'required': True},
            'slug': {'read_only': True},
        }

    def get_image_url(self, obj):
        try:
            # Verificar se a receita tem imagens associadas
            primary_image = obj.images.filter(is_primary=True).first()
            if not primary_image:
                primary_image = obj.images.first()
                
            if primary_image and primary_image.image:
                # Cloudinary já fornece URLs completas, não precisamos de build_absolute_uri
                return str(primary_image.image.url)
        except Exception as e:
            import logging
            logger = logging.getLogger('django')
            logger.error(f"Erro ao obter URL da imagem: {str(e)}")
        return None