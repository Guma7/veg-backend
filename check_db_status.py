#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.core.management.commands.migrate import Command as MigrateCommand
from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand
from django.apps import apps
from django.contrib.auth.models import User
from users.models import UserProfile
from recipes.models import Recipe

def check_database_connection():
    """Verifica a conexão com o banco de dados"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexão com banco de dados: OK")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco de dados: {e}")
        return False

def list_tables():
    """Lista todas as tabelas no banco de dados"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"\n📋 Tabelas no banco de dados ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
            return tables
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")
        return []

def check_specific_tables():
    """Verifica se tabelas específicas existem"""
    required_tables = [
        'auth_user',
        'users_userprofile', 
        'recipes_recipe'
    ]
    
    print("\n🔍 Verificando tabelas específicas:")
    
    for table in required_tables:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
                print(f"  ✅ {table}: EXISTS")
        except Exception as e:
            print(f"  ❌ {table}: NOT EXISTS - {e}")

def check_recipe_slug_column():
    """Verifica se a coluna slug existe na tabela recipes_recipe"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'recipes_recipe' 
                AND column_name = 'slug';
            """)
            result = cursor.fetchone()
            if result:
                print("  ✅ recipes_recipe.slug: EXISTS")
            else:
                print("  ❌ recipes_recipe.slug: NOT EXISTS")
    except Exception as e:
        print(f"  ❌ Erro ao verificar coluna slug: {e}")

def show_migration_status():
    """Mostra o status das migrações"""
    print("\n📊 Status das migrações:")
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capturar output do showmigrations
        output = StringIO()
        call_command('showmigrations', stdout=output)
        migrations_output = output.getvalue()
        print(migrations_output)
        
    except Exception as e:
        print(f"❌ Erro ao verificar migrações: {e}")

def test_model_operations():
    """Testa operações básicas nos modelos"""
    print("\n🧪 Testando operações nos modelos:")
    
    # Testar User
    try:
        user_count = User.objects.count()
        print(f"  ✅ User.objects.count(): {user_count}")
    except Exception as e:
        print(f"  ❌ Erro ao contar usuários: {e}")
    
    # Testar UserProfile
    try:
        profile_count = UserProfile.objects.count()
        print(f"  ✅ UserProfile.objects.count(): {profile_count}")
    except Exception as e:
        print(f"  ❌ Erro ao contar perfis: {e}")
    
    # Testar Recipe
    try:
        recipe_count = Recipe.objects.count()
        print(f"  ✅ Recipe.objects.count(): {recipe_count}")
    except Exception as e:
        print(f"  ❌ Erro ao contar receitas: {e}")

def main():
    print("🔍 VERIFICAÇÃO DO STATUS DO BANCO DE DADOS")
    print("=" * 50)
    
    # Verificar conexão
    if not check_database_connection():
        return
    
    # Listar todas as tabelas
    tables = list_tables()
    
    # Verificar tabelas específicas
    check_specific_tables()
    
    # Verificar coluna slug
    check_recipe_slug_column()
    
    # Mostrar status das migrações
    show_migration_status()
    
    # Testar operações nos modelos
    test_model_operations()
    
    print("\n" + "=" * 50)
    print("✅ Verificação concluída!")

if __name__ == '__main__':
    main()