#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection, transaction
from django.core.management import call_command
from django.apps import apps
from django.contrib.auth.models import User

def check_table_exists(table_name):
    """Verifica se uma tabela existe no banco de dados"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            return True
    except Exception:
        return False

def check_column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, [table_name, column_name])
            return cursor.fetchone() is not None
    except Exception:
        return False

def apply_migrations_for_app(app_name):
    """Aplica migrações para um app específico"""
    try:
        print(f"📦 Aplicando migrações para {app_name}...")
        call_command('migrate', app_name, verbosity=2)
        print(f"✅ Migrações do {app_name} aplicadas com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações do {app_name}: {e}")
        return False

def create_missing_tables():
    """Cria tabelas que estão faltando"""
    print("🔧 CORRIGINDO TABELAS FALTANTES")
    print("=" * 50)
    
    # Verificar e corrigir tabela users_userprofile
    if not check_table_exists('users_userprofile'):
        print("❌ Tabela users_userprofile não existe")
        print("🔧 Aplicando migrações do app users...")
        
        # Aplicar migrações do users
        if apply_migrations_for_app('users'):
            if check_table_exists('users_userprofile'):
                print("✅ Tabela users_userprofile criada com sucesso")
            else:
                print("❌ Falha ao criar tabela users_userprofile")
                return False
        else:
            return False
    else:
        print("✅ Tabela users_userprofile já existe")
    
    # Verificar e corrigir coluna slug na tabela recipes_recipe
    if check_table_exists('recipes_recipe'):
        if not check_column_exists('recipes_recipe', 'slug'):
            print("❌ Coluna slug não existe na tabela recipes_recipe")
            print("🔧 Aplicando migrações do app recipes...")
            
            # Aplicar migrações do recipes
            if apply_migrations_for_app('recipes'):
                if check_column_exists('recipes_recipe', 'slug'):
                    print("✅ Coluna slug criada com sucesso")
                else:
                    print("❌ Falha ao criar coluna slug")
                    return False
            else:
                return False
        else:
            print("✅ Coluna slug já existe na tabela recipes_recipe")
    else:
        print("❌ Tabela recipes_recipe não existe")
        print("🔧 Aplicando migrações do app recipes...")
        
        if apply_migrations_for_app('recipes'):
            print("✅ Tabela recipes_recipe criada")
        else:
            return False
    
    return True

def apply_all_migrations():
    """Aplica todas as migrações pendentes"""
    try:
        print("\n🚀 Aplicando todas as migrações pendentes...")
        call_command('migrate', verbosity=2)
        print("✅ Todas as migrações aplicadas com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        return False

def verify_final_state():
    """Verifica o estado final das tabelas"""
    print("\n🔍 VERIFICAÇÃO FINAL")
    print("=" * 30)
    
    # Verificar tabelas essenciais
    essential_tables = [
        'auth_user',
        'users_userprofile',
        'recipes_recipe'
    ]
    
    all_good = True
    for table in essential_tables:
        if check_table_exists(table):
            print(f"✅ {table}: EXISTS")
        else:
            print(f"❌ {table}: NOT EXISTS")
            all_good = False
    
    # Verificar coluna slug
    if check_column_exists('recipes_recipe', 'slug'):
        print("✅ recipes_recipe.slug: EXISTS")
    else:
        print("❌ recipes_recipe.slug: NOT EXISTS")
        all_good = False
    
    return all_good

def test_model_creation():
    """Testa a criação de modelos"""
    print("\n🧪 TESTANDO CRIAÇÃO DE MODELOS")
    print("=" * 35)
    
    try:
        # Testar criação de usuário
        test_user = User.objects.create_user(
            username='test_deploy_user',
            email='test@deploy.com',
            password='testpass123'
        )
        print("✅ Usuário de teste criado com sucesso")
        
        # Verificar se o perfil foi criado automaticamente
        from users.models import UserProfile
        if hasattr(test_user, 'profile'):
            print("✅ Perfil do usuário criado automaticamente")
        else:
            print("⚠️ Perfil não foi criado automaticamente, criando manualmente...")
            UserProfile.objects.create(user=test_user)
            print("✅ Perfil criado manualmente")
        
        # Testar criação de receita
        from recipes.models import Recipe
        test_recipe = Recipe.objects.create(
            title='Receita de Teste Deploy',
            description='Teste de deploy',
            instructions='Instruções de teste',
            prep_time=10,
            cook_time=20,
            servings=2,
            author=test_user
        )
        print("✅ Receita de teste criada com sucesso")
        
        if test_recipe.slug:
            print(f"✅ Slug gerado automaticamente: {test_recipe.slug}")
        else:
            print("❌ Slug não foi gerado")
        
        # Limpar dados de teste
        test_recipe.delete()
        test_user.delete()
        print("✅ Dados de teste removidos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar modelos: {e}")
        return False

def main():
    print("🔧 SCRIPT DE CORREÇÃO DE TABELAS FALTANTES")
    print("=" * 55)
    
    # Etapa 1: Corrigir tabelas faltantes
    if not create_missing_tables():
        print("❌ Falha ao corrigir tabelas faltantes")
        sys.exit(1)
    
    # Etapa 2: Aplicar todas as migrações
    if not apply_all_migrations():
        print("❌ Falha ao aplicar migrações")
        sys.exit(1)
    
    # Etapa 3: Verificar estado final
    if not verify_final_state():
        print("❌ Verificação final falhou")
        sys.exit(1)
    
    # Etapa 4: Testar criação de modelos
    if not test_model_creation():
        print("❌ Teste de modelos falhou")
        sys.exit(1)
    
    print("\n" + "=" * 55)
    print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("✅ Todas as tabelas e colunas estão funcionando corretamente")

if __name__ == '__main__':
    main()