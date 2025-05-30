from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['description', 'profile_image', 'social_links', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    
    # Substituir o validador padrão do Django para permitir espaços
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^[\w\s]+$',
                message='O nome de usuário pode conter apenas letras, números, sublinhados e espaços.',
                code='invalid_username'
            ),
        ]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate_username(self, value):
        # Verificar se o nome de usuário já existe
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nome de usuário já está em uso.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este email já está cadastrado.')
        return value

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password']
            )
            # O perfil é criado automaticamente pelo signal post_save
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Erro ao criar usuário: {str(e)}")