#!/usr/bin/env python
"""
Script para testar as validações de usuário e identificar problemas.
"""

import os
import django
from django.contrib.auth.models import User
from users.serializers import UserSerializer

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_user_validation():
    """Testa as validações do serializer de usuário"""
    print("=== Teste de Validações de Usuário ===")
    
    # Teste 1: Senha muito curta
    print("\n1. Testando senha muito curta (menos de 8 caracteres):")
    data = {
        'username': 'testeuser',
        'email': 'teste@example.com',
        'password': '123'  # Senha muito curta
    }
    
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        print("✓ Validação passou (inesperado)")
    else:
        print("✗ Validação falhou (esperado):")
        for field, errors in serializer.errors.items():
            print(f"  - {field}: {errors}")
    
    # Teste 2: Senha válida
    print("\n2. Testando senha válida (8+ caracteres):")
    data = {
        'username': 'testeuser2',
        'email': 'teste2@example.com',
        'password': 'senhavalida123'  # Senha válida
    }
    
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        print("✓ Validação passou (esperado)")
    else:
        print("✗ Validação falhou (inesperado):")
        for field, errors in serializer.errors.items():
            print(f"  - {field}: {errors}")
    
    # Teste 3: Email inválido
    print("\n3. Testando email inválido:")
    data = {
        'username': 'testeuser3',
        'email': 'email_invalido',  # Email inválido
        'password': 'senhavalida123'
    }
    
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        print("✓ Validação passou (inesperado)")
    else:
        print("✗ Validação falhou (esperado):")
        for field, errors in serializer.errors.items():
            print(f"  - {field}: {errors}")
    
    # Teste 4: Username com caracteres especiais
    print("\n4. Testando username com caracteres especiais:")
    data = {
        'username': 'teste@user!',  # Username inválido
        'email': 'teste4@example.com',
        'password': 'senhavalida123'
    }
    
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        print("✓ Validação passou (inesperado)")
    else:
        print("✗ Validação falhou (esperado):")
        for field, errors in serializer.errors.items():
            print(f"  - {field}: {errors}")
    
    # Teste 5: Dados válidos completos
    print("\n5. Testando dados completamente válidos:")
    data = {
        'username': 'usuarioteste',
        'email': 'usuarioteste@example.com',
        'password': 'minhasenhasegura123'
    }
    
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        print("✓ Validação passou (esperado)")
        print("  Dados validados:", serializer.validated_data)
    else:
        print("✗ Validação falhou (inesperado):")
        for field, errors in serializer.errors.items():
            print(f"  - {field}: {errors}")

def test_existing_users():
    """Verifica se há usuários existentes no banco"""
    print("\n=== Verificação de Usuários Existentes ===")
    
    try:
        users = User.objects.all()
        print(f"Total de usuários no banco: {users.count()}")
        
        if users.exists():
            print("Usuários existentes:")
            for user in users[:5]:  # Mostrar apenas os primeiros 5
                print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")
        else:
            print("Nenhum usuário encontrado no banco de dados.")
            
    except Exception as e:
        print(f"Erro ao consultar usuários: {e}")

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("=== Teste de Conexão com Banco de Dados ===")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Conexão com banco de dados estabelecida")
            
            # Verificar se a tabela auth_user existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user'
                );
            """)
            auth_user_exists = cursor.fetchone()[0]
            print(f"✓ Tabela auth_user existe: {auth_user_exists}")
            
            return True
    except Exception as e:
        print(f"✗ Erro na conexão com banco de dados: {e}")
        return False

if __name__ == '__main__':
    print("=== Script de Teste de Validações ===")
    
    # Testar conexão com banco
    if not test_database_connection():
        print("\n⚠️  Não foi possível conectar ao banco de dados.")
        print("Este script deve ser executado no ambiente de produção (Render).")
    else:
        # Testar usuários existentes
        test_existing_users()
    
    # Testar validações (funciona mesmo sem conexão com banco)
    test_user_validation()
    
    print("\n=== Teste Concluído ===")