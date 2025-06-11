from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
import json
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    """Endpoint para obter um token CSRF"""
    token = get_token(request)
    logger.info(f"Token CSRF gerado: {token}")
    logger.info(f"Comprimento do token CSRF: {len(token)}")
    logger.info(f"Cookies na requisição: {request.COOKIES}")
    logger.info(f"Headers da requisição: {dict(request.headers)}")
    return JsonResponse({'csrfToken': token})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_info(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Autenticação necessária'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acesso não autenticado para registro
def register_user(request):
    """
    Registra um novo usuário.
    """
    try:
        logger.info(f"Tentativa de registro - Dados recebidos: {request.data}")
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                logger.info(f"Usuário registrado com sucesso: {user.username}")
                user = authenticate(
                    username=request.data.get('username'),
                    password=request.data.get('password')
                )
                if user:
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'user': UserSerializer(user).data,
                        'message': 'Registro realizado com sucesso',
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({
                        'user': UserSerializer(user).data,
                        'message': 'Usuário registrado com sucesso, mas falha ao autenticar automaticamente.'
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Erro ao salvar usuário: {str(e)}")
                # Tratamento específico para erro de duplicidade de perfil
                if 'duplicate key value violates unique constraint' in str(e) or 'violates unique constraint' in str(e):
                    return Response({
                        'error': 'Já existe um perfil para este usuário.',
                        'message': 'Erro ao registrar usuário: perfil duplicado',
                        'status_code': 400
                    }, status=status.HTTP_400_BAD_REQUEST)
                return Response({
                    'error': str(e),
                    'message': 'Erro ao registrar usuário'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Retornar erros de validação de forma mais detalhada
        error_messages = {}
        for field, errors in serializer.errors.items():
            error_messages[field] = str(errors[0]) if errors else 'Campo inválido'
        
        logger.error(f"Erros de validação: {error_messages}")
        
        return Response({
            'error': 'Erro de validação',
            'detail': error_messages
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erro não tratado durante o registro: {str(e)}")
        return Response({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado durante o registro',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acesso não autenticado explicitamente
def login_user(request):
    try:
        identifier = request.data.get('identifier')
        password = request.data.get('password')
        
        logger.info(f"Tentativa de login com identificador: {identifier}")
        
        # Verificar se o identificador é um email ou nome de usuário
        if '@' in identifier:
            # Tentar autenticar com email
            try:
                user_obj = User.objects.get(email=identifier)
                username = user_obj.username
            except User.DoesNotExist:
                logger.warning(f"Usuário não encontrado com email: {identifier}")
                return Response(
                    {'error': 'Usuário não encontrado com este email'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            # Usar o identificador como nome de usuário
            username = identifier
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            # Incluir dados do usuário na resposta para evitar deslogamento automático
            serializer = UserSerializer(user)
            logger.info(f"Login bem-sucedido para usuário: {username}")
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': serializer.data
            })
        
        logger.warning(f"Credenciais inválidas para usuário: {username}")
        return Response(
            {'error': 'Credenciais inválidas'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        logger.error(f"Erro não tratado durante o login: {str(e)}")
        return Response({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado durante o login',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def logout_user(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Autenticação necessária'}, status=status.HTTP_401_UNAUTHORIZED)
    logout(request)
    return Response({'message': 'Logged out successfully'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def delete_all_users(request):
    try:
        # Excluir todos os perfis de usuário
        UserProfile.objects.all().delete()
        # Excluir todos os usuários, exceto o superusuário
        User.objects.filter(is_superuser=False).delete()
        return Response({'message': 'Todos os usuários foram excluídos com sucesso'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Erro ao excluir usuários: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'PATCH', 'OPTIONS'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_profile(request):
    """Atualiza o perfil do usuário."""
    user = request.user
    profile = user.profile
    
    # Log para depuração
    print(f"Dados recebidos: {request.data}")
    print(f"Arquivos recebidos: {request.FILES}")
    
    # Atualizar descrição
    if 'description' in request.data:
        profile.description = request.data['description']
    
    # Atualizar links sociais
    if 'social_links' in request.data:
        try:
            # Verificar se já é um dicionário ou se precisa ser convertido de string JSON
            if isinstance(request.data['social_links'], dict):
                social_links = request.data['social_links']
            else:
                social_links = json.loads(request.data['social_links'])
            profile.social_links = social_links
        except json.JSONDecodeError:
            return Response(
                {'error': 'Formato inválido para social_links'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Processar imagem de perfil (Cloudinary gerencia automaticamente)
    try:
        if 'profile_image' in request.FILES:
            # O Cloudinary automaticamente substitui a imagem anterior
            profile.profile_image = request.FILES['profile_image']
            logger.info(f"Imagem de perfil salva com sucesso no Cloudinary: {profile.profile_image}")
        elif 'profile_picture' in request.FILES:
            # Nome alternativo para compatibilidade
            profile.profile_image = request.FILES['profile_picture']
            logger.info(f"Imagem de perfil salva com sucesso no Cloudinary: {profile.profile_image}")
        elif 'remove_profile_image' in request.data or 'remove_profile_picture' in request.data:
            # Remover imagem de perfil (Cloudinary gerencia a remoção)
            profile.profile_image = None
            logger.info("Imagem de perfil removida")
    except Exception as e:
        logger.error(f"Erro ao processar imagem de perfil: {str(e)}")
        return Response({'error': f'Erro ao processar imagem: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    profile.save()
    
    # Retornar dados atualizados
    serializer = UserProfileSerializer(profile)
    
    # Adicionar URL da imagem de perfil (Cloudinary fornece URL completa)
    data = serializer.data
    if profile.profile_image:
        # Cloudinary já fornece URL completa, não precisa de build_absolute_uri
        data['profile_image'] = str(profile.profile_image.url)
    
    # Adicionar campos adicionais para compatibilidade com o frontend
    data['profileImage'] = data.get('profile_image')
    data['socialLinks'] = data.get('social_links')
    
    return Response(data)

@api_view(['POST'])
def change_password(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Autenticação necessária'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Verificar se as senhas foram fornecidas
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not current_password or not new_password:
        return Response(
            {'error': 'Senha atual e nova senha são obrigatórias'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar se a senha atual está correta
    user = request.user
    if not user.check_password(current_password):
        return Response(
            {'error': 'Senha atual incorreta'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Alterar a senha
    user.set_password(new_password)
    user.save()
    
    # Gerar novos tokens JWT para manter o usuário logado
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Senha alterada com sucesso',
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_by_username(request, username):
    try:
        user = User.objects.get(username=username)
        profile = getattr(user, 'profile', None)
        if not profile:
            return Response({'error': 'Perfil não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Combinar dados do usuário e perfil
        user_data = {
            'id': user.id,
            'username': user.username,
            'description': profile.description,
            'socialLinks': profile.social_links or {}
        }
        
        # Tratar a URL da imagem de perfil (Cloudinary)
        if profile.profile_image and hasattr(profile.profile_image, 'url'):
            # Cloudinary já fornece URL completa
            user_data['profileImage'] = str(profile.profile_image.url)
        else:
            user_data['profileImage'] = request.build_absolute_uri('/media/default/default_profile.svg')
        
        return Response(user_data)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)