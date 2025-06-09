from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Recipe, Rating, RecipeImage
from users.models import UserProfile
from .serializers import (
    RecipeSerializer, RatingSerializer, UserProfileSerializer,
    UserSerializer
)
from rest_framework.views import APIView
from django.db.models import Avg, Q
from django.contrib.auth.models import User
from rest_framework import permissions



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def perform_create(self, serializer):
        # Verificar se já existe um perfil para este usuário
        if not UserProfile.objects.filter(user=self.request.user).exists():
            serializer.save(user=self.request.user)
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Já existe um perfil para este usuário.')

@api_view(['GET'])
def recipe_by_slug(request, slug):
    """Endpoint para buscar uma receita pelo seu slug"""
    try:
        recipe = Recipe.objects.get(slug=slug)
        recipe.increment_views()
        serializer = RecipeSerializer(recipe, context={'request': request})
        return Response(serializer.data)
    except Recipe.DoesNotExist:
        return Response({"error": "Receita não encontrada"}, status=status.HTTP_404_NOT_FOUND)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.annotate(
        average_rating=Avg('ratings__score')
    ).order_by('-average_rating')
    lookup_field = 'slug'  # Usar slug como campo de busca ao invés de id
    serializer_class = RecipeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    def perform_create(self, serializer):
        # Obter imagens do request
        images = self.request.FILES.getlist('images')
        single_image = self.request.FILES.get('image')
        
        # Adicionar logs para depuração
        import logging
        logger = logging.getLogger('django')
        logger.info(f"Processando upload de receita: {len(images)} imagens na lista, imagem única: {single_image is not None}")
        
        # Verificar se há pelo menos uma imagem
        if not images and not single_image:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('At least one image is required')
        
        # Salvar a receita
        recipe = serializer.save(author=self.request.user)
        
        # Processar imagens da lista
        for index, image in enumerate(images):
            try:
                RecipeImage.objects.create(
                    recipe=recipe,
                    image=image,
                    is_primary=(index == 0)
                )
                logger.info(f"Imagem {index} salva com sucesso: {image.name}")
            except Exception as e:
                logger.error(f"Erro ao salvar imagem {index}: {str(e)}")
        
        # Processar imagem única se existir e não houver imagens na lista
        if single_image and not images:
            try:
                RecipeImage.objects.create(
                    recipe=recipe,
                    image=single_image,
                    is_primary=True
                )
                logger.info(f"Imagem única salva com sucesso: {single_image.name}")
            except Exception as e:
                logger.error(f"Erro ao salvar imagem única: {str(e)}")


    @action(detail=True, methods=['post'])
    def update_images(self, request, slug=None):
        recipe = self.get_object()
        images = request.FILES.getlist('images')
        primary_index = request.data.get('primary_index', 0)
        
        # Adicionar logs para depuração
        import logging
        logger = logging.getLogger('django')
        logger.info(f"Atualizando imagens da receita {recipe.id}: {len(images)} imagens na lista")
        
        if images:
            try:
                # Update existing images
                recipe.images.all().delete()
                logger.info(f"Imagens anteriores da receita {recipe.id} foram excluídas")
                
                for index, image in enumerate(images):
                    try:
                        RecipeImage.objects.create(
                            recipe=recipe,
                            image=image,
                            is_primary=(index == int(primary_index))
                        )
                        logger.info(f"Imagem {index} atualizada com sucesso: {image.name}, primária: {index == int(primary_index)}")
                    except Exception as e:
                        logger.error(f"Erro ao atualizar imagem {index}: {str(e)}")
            except Exception as e:
                logger.error(f"Erro ao processar atualização de imagens: {str(e)}")
                return Response({'error': 'Erro ao atualizar imagens'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning(f"Tentativa de atualizar imagens sem enviar novas imagens para a receita {recipe.id}")
        
        return Response(self.get_serializer(recipe).data)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'recipe_class', 'style', 'genre', 'nutritional_level', 'does_not_contain', 'traditional', 'ingredients']
    
    @action(detail=False, methods=['get'])
    def s_suggest(self, request):
        query = request.query_params.get('query', '')
        if len(query) < 2:
            return Response([])
            
        # Buscar gêneros existentes que começam com a consulta
        genres = Recipe.objects.filter(genre__istartswith=query)\
            .values_list('genre', flat=True).distinct()
        
        # Limitar a 10 sugestões
        suggestions = list(genres)[:10]
        return Response(suggestions)

    # Método perform_create já está definido acima

    @action(detail=True, methods=['post'])
    def rate(self, request, slug=None):
        recipe = self.get_object()
        score = request.data.get('score')
        
        try:
            score = int(score)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Score must be a valid number between 1 and 10'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not (1 <= score <= 10):
            return Response(
                {'error': 'Score must be between 1 and 10'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rating, created = Rating.objects.update_or_create(
            recipe=recipe,
            user=request.user,
            defaults={'score': score}
        )
        
        return Response({
            'rating': RatingSerializer(rating).data,
            'average_rating': recipe.average_rating
        })

    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        recipe = self.get_object()
        similar_recipes = Recipe.objects.filter(
            Q(recipe_class=recipe.recipe_class) |
            Q(recipe_genre=recipe.recipe_genre)
        ).exclude(id=recipe.id).annotate(
            avg_rating=Avg('ratings__score')
        ).order_by('-avg_rating')[:4]
        
        serializer = self.get_serializer(similar_recipes, many=True)
        return Response(serializer.data)




@api_view(['GET'])
@permission_classes([AllowAny])
def search_recipes(request):
    # Parâmetros de paginação
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 30))
    
    # Parâmetros de busca
    search = request.GET.get('search', '')
    recipe_class = request.GET.get('recipe_class', '')
    style = request.GET.get('style', '')
    genre = request.GET.get('genre', '')
    nutritional_level = request.GET.get('nutritional_level', '')
    does_not_contain = request.GET.get('does_not_contain', '')
    traditional = request.GET.get('traditional', '')
    ingredients = request.GET.get('ingredients', '')
    
    # Iniciar a consulta
    recipes = Recipe.objects.all().annotate(average_rating=Avg('ratings__score'))
    
    # Aplicar filtros
    if search:
        recipes = recipes.filter(
            Q(title__icontains=search) |
            Q(ingredients__icontains=search) |
            Q(instructions__icontains=search)
        )
    
    if recipe_class:
        recipes = recipes.filter(recipe_class=recipe_class)
    
    if style:
        recipes = recipes.filter(style=style)
    
    if genre:
        recipes = recipes.filter(genre__icontains=genre)
    
    if nutritional_level:
        recipes = recipes.filter(nutritional_level=nutritional_level)
    
    if does_not_contain:
        recipes = recipes.filter(does_not_contain__icontains=does_not_contain)
    
    if traditional:
        recipes = recipes.filter(traditional__icontains=traditional)
    
    if ingredients:
        # Dividir a string de ingredientes em uma lista
        ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
        # Criar uma consulta para cada ingrediente
        for ingredient in ingredient_list:
            recipes = recipes.filter(ingredients__icontains=ingredient)
    
    # Ordenar por avaliação média
    recipes = recipes.order_by('-average_rating', '-created_at')
    
    # Contar o total de receitas
    total_count = recipes.count()
    
    # Calcular o total de páginas
    total_pages = (total_count + limit - 1) // limit
    
    # Aplicar paginação
    start = (page - 1) * limit
    end = start + limit
    paginated_recipes = recipes[start:end]
    
    # Serializar os resultados
    serializer = RecipeSerializer(paginated_recipes, many=True, context={'request': request})
    
    # Retornar resposta com metadados de paginação
    return Response({
        'results': serializer.data,
        'count': total_count,
        'total_pages': total_pages,
        'current_page': page
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def suggest_tags(request):
    query = request.GET.get('query', '').lower()
    if not query or len(query) < 2:
        return Response([])

    # Busca gêneros existentes
    genres = Recipe.objects.filter(
        genre__icontains=query
    ).values_list('genre', flat=True).distinct()[:10]

    # Processa e remove duplicatas
    suggestions = set(genres)

    return Response(sorted(list(suggestions)))

@api_view(['GET'])
def user_recipes(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    recipes = Recipe.objects.filter(author=user).annotate(
        average_rating=Avg('ratings__score')
    ).order_by('-created_at')
    
    serializer = RecipeSerializer(recipes, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
def get_categories(request):
    return Response({
        'classes': [
            {'value': 'gourmet', 'label': 'Gourmet'},
            {'value': 'caseira', 'label': 'Caseira'}
        ],

        'genres': [
            {'value': 'entrada', 'label': 'Entrada'},
            {'value': 'prato_principal', 'label': 'Prato Principal'},
            {'value': 'sobremesa', 'label': 'Sobremesa'}
        ]
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def rate_recipe(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        score = request.data.get('score')
        
        if not isinstance(score, int) or not (1 <= score <= 10):
            return Response(
                {'error': 'Score must be an integer between 1 and 10'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        rating, created = Rating.objects.update_or_create(
            recipe=recipe,
            user=request.user,
            defaults={'score': score}
        )

        return Response({
            'average_rating': recipe.average_rating,
            'total_ratings': recipe.total_ratings,
            'user_rating': score
        })
    except Recipe.DoesNotExist:
        return Response(
            {'error': 'Recipe not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_recipe_ratings(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        user_rating = None
        if request.user.is_authenticated:
            rating = Rating.objects.filter(
                recipe=recipe, 
                user=request.user
            ).first()
            user_rating = rating.score if rating else None

        return Response({
            'average_rating': recipe.average_rating,
            'total_ratings': recipe.total_ratings,
            'user_rating': user_rating
        })
    except Recipe.DoesNotExist:
        return Response(
            {'error': 'Recipe not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_recipes(request):
    try:
        # Como o campo is_featured não existe mais, vamos selecionar as receitas mais populares
        # baseado em visualizações ou avaliações
        recipes = Recipe.objects.all()\
            .select_related('author')\
            .prefetch_related('ratings', 'images')\
            .annotate(average_rating=Avg('ratings__score'))\
            .order_by('-views_count', '-average_rating')[:5]
            
        # Garantir que o contexto da requisição seja passado para o serializer
        serializer = RecipeSerializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)
    except Exception as e:
        # Logar o erro para facilitar a depuração
        import logging
        logger = logging.getLogger('django')
        logger.error(f"Erro ao buscar receitas em destaque: {str(e)}")
        return Response({'error': 'Erro ao processar receitas em destaque'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
