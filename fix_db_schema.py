#!/usr/bin/env python
"""
Script para verificar e corrigir problemas específicos no esquema do banco de dados:
1. Tabela users_userprofile ausente
2. Coluna slug ausente na tabela recipes_recipe

Este script deve ser executado no ambiente de produção do Render.
"""

import os
import sys
import django
import uuid
from django.db import connection, transaction
from django.core.management import call_command

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def check_table_exists(table_name):
    """Verifica se uma tabela existe no banco de dados"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, [table_name])
            exists = cursor.fetchone()[0]
            return exists
    except Exception as e:
        print(f"❌ Erro ao verificar tabela {table_name}: {e}")
        return False

def check_column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    AND column_name = %s
                );
            """, [table_name, column_name])
            exists = cursor.fetchone()[0]
            return exists
    except Exception as e:
        print(f"❌ Erro ao verificar coluna {column_name} na tabela {table_name}: {e}")
        return False

def create_userprofile_table():
    """Cria a tabela users_userprofile se não existir"""
    if check_table_exists('users_userprofile'):
        print("✅ Tabela users_userprofile já existe")
        return True
    
    print("🔧 Criando tabela users_userprofile...")
    try:
        # Aplicar migrações do app users
        call_command('migrate', 'users', verbosity=2)
        
        # Verificar se a tabela foi criada
        if check_table_exists('users_userprofile'):
            print("✅ Tabela users_userprofile criada com sucesso")
            return True
        else:
            print("❌ Falha ao criar tabela users_userprofile via migrações")
            
            # Tentar criar manualmente como último recurso
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE users_userprofile (
                            id SERIAL PRIMARY KEY,
                            description TEXT NOT NULL DEFAULT '',
                            profile_image VARCHAR(100) NULL,
                            social_links JSONB NOT NULL DEFAULT '{}',
                            created_at TIMESTAMP WITH TIME ZONE NULL,
                            updated_at TIMESTAMP WITH TIME ZONE NULL,
                            user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE
                        );
                    """)
                print("✅ Tabela users_userprofile criada manualmente")
                return True
            except Exception as e:
                print(f"❌ Erro ao criar tabela manualmente: {e}")
                return False
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações do users: {e}")
        return False

def add_slug_column():
    """Adiciona a coluna slug à tabela recipes_recipe se não existir"""
    if not check_table_exists('recipes_recipe'):
        print("❌ Tabela recipes_recipe não existe. Aplicando migrações do recipes primeiro...")
        try:
            call_command('migrate', 'recipes', verbosity=2)
            if not check_table_exists('recipes_recipe'):
                print("❌ Falha ao criar tabela recipes_recipe")
                return False
        except Exception as e:
            print(f"❌ Erro ao aplicar migrações do recipes: {e}")
            return False
    
    if check_column_exists('recipes_recipe', 'slug'):
        print("✅ Coluna slug já existe na tabela recipes_recipe")
        return True
    
    print("🔧 Adicionando coluna slug à tabela recipes_recipe...")
    try:
        # Aplicar migrações específicas do recipes
        call_command('migrate', 'recipes', '0005_add_recipe_slug_field', verbosity=2)
        call_command('migrate', 'recipes', '0006_populate_recipe_slugs', verbosity=2)
        
        # Verificar se a coluna foi criada
        if check_column_exists('recipes_recipe', 'slug'):
            print("✅ Coluna slug adicionada com sucesso")
            return True
        else:
            print("❌ Falha ao adicionar coluna slug via migrações")
            
            # Tentar adicionar manualmente como último recurso
            try:
                with connection.cursor() as cursor:
                    # Adicionar coluna
                    cursor.execute("ALTER TABLE recipes_recipe ADD COLUMN slug VARCHAR(255) UNIQUE;")
                    
                    # Gerar slugs para receitas existentes
                    cursor.execute("SELECT id, title FROM recipes_recipe WHERE slug IS NULL OR slug = '';")
                    recipes = cursor.fetchall()
                    
                    for recipe_id, title in recipes:
                        # Gerar slug a partir do título
                        from django.utils.text import slugify
                        slug_base = slugify(title)
                        slug = f"{slug_base}-{str(uuid.uuid4())[:8]}"
                        
                        # Atualizar receita com o novo slug
                        cursor.execute("UPDATE recipes_recipe SET slug = %s WHERE id = %s;", [slug, recipe_id])
                    
                print(f"✅ Coluna slug adicionada manualmente e {len(recipes)} receitas atualizadas")
                return True
            except Exception as e:
                print(f"❌ Erro ao adicionar coluna manualmente: {e}")
                return False
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações do recipes: {e}")
        return False

def create_missing_profiles():
    """Cria perfis para usuários que não têm"""
    try:
        from django.contrib.auth.models import User
        from users.models import UserProfile
        
        # Encontrar usuários sem perfil
        users_without_profile = []
        for user in User.objects.all():
            try:
                # Tentar acessar o perfil
                profile = user.profile
            except Exception:
                # Se der erro, adicionar à lista
                users_without_profile.append(user)
        
        if not users_without_profile:
            print("✅ Todos os usuários já têm perfil")
            return True
        
        print(f"🔧 Criando perfis para {len(users_without_profile)} usuários...")
        for user in users_without_profile:
            try:
                UserProfile.objects.create(user=user)
                print(f"  ✅ Perfil criado para {user.username}")
            except Exception as e:
                print(f"  ❌ Erro ao criar perfil para {user.username}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar perfis faltantes: {e}")
        return False

def main():
    print("🔧 CORREÇÃO DE PROBLEMAS NO ESQUEMA DO BANCO DE DADOS")
    print("=" * 50)
    
    # Verificar conexão com o banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL: {version}")
    except Exception as e:
        print(f"❌ Erro na conexão com o banco de dados: {e}")
        sys.exit(1)
    
    # Corrigir tabela users_userprofile
    print("\n🔍 Verificando tabela users_userprofile...")
    if not create_userprofile_table():
        print("❌ Falha ao criar tabela users_userprofile")
        sys.exit(1)
    
    # Corrigir coluna slug
    print("\n🔍 Verificando coluna slug na tabela recipes_recipe...")
    if not add_slug_column():
        print("❌ Falha ao adicionar coluna slug")
        sys.exit(1)
    
    # Criar perfis faltantes
    print("\n🔍 Verificando perfis de usuário...")
    create_missing_profiles()
    
    print("\n" + "=" * 50)
    print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == '__main__':
    main()