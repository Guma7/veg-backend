#!/usr/bin/env python
"""
Script para corrigir conflitos de migração no banco de dados Neon.
Este script verifica e sincroniza o estado das migrações com o banco de dados.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.base import BaseCommand

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import transaction
from recipes.models import Recipe, RecipeImage

def check_table_exists(table_name):
    """Verifica se uma tabela existe no banco de dados."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def check_column_exists(table_name, column_name):
    """Verifica se uma coluna existe em uma tabela."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            );
        """, [table_name, column_name])
        return cursor.fetchone()[0]

def fix_recipeimage_table():
    """Corrige a estrutura da tabela recipes_recipeimage."""
    print("Verificando estrutura da tabela recipes_recipeimage...")
    
    with connection.cursor() as cursor:
        # Verificar se a tabela existe
        if not check_table_exists('recipes_recipeimage'):
            print("Criando tabela recipes_recipeimage...")
            cursor.execute("""
                CREATE TABLE recipes_recipeimage (
                    id BIGSERIAL PRIMARY KEY,
                    image VARCHAR(255) NOT NULL,
                    recipe_id BIGINT NOT NULL REFERENCES recipes_recipe(id) ON DELETE CASCADE,
                    is_primary BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                CREATE INDEX recipes_recipeimage_recipe_id_idx ON recipes_recipeimage(recipe_id);
            """)
            print("Tabela recipes_recipeimage criada com sucesso.")
        else:
            print("Tabela recipes_recipeimage já existe. Verificando colunas...")
            
            # Verificar e adicionar colunas necessárias
            if not check_column_exists('recipes_recipeimage', 'is_primary'):
                print("Adicionando coluna is_primary...")
                cursor.execute("ALTER TABLE recipes_recipeimage ADD COLUMN is_primary BOOLEAN DEFAULT FALSE;")
            
            if not check_column_exists('recipes_recipeimage', 'created_at'):
                if check_column_exists('recipes_recipeimage', 'uploaded_at'):
                    print("Renomeando uploaded_at para created_at...")
                    cursor.execute("ALTER TABLE recipes_recipeimage RENAME COLUMN uploaded_at TO created_at;")
                else:
                    print("Adicionando coluna created_at...")
                    cursor.execute("ALTER TABLE recipes_recipeimage ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
            
            if not check_column_exists('recipes_recipeimage', 'updated_at'):
                print("Adicionando coluna updated_at...")
                cursor.execute("ALTER TABLE recipes_recipeimage ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();")

def mark_migrations_as_applied():
    """Marca as migrações como aplicadas no banco de dados."""
    print("Marcando migrações como aplicadas...")
    
    migrations_to_mark = [
        ('recipes', '0003_add_recipeimage_table'),
        ('recipes', '0004_add_is_primary_field'),
        ('recipes', '0005_add_recipe_slug_field'),
        ('recipes', '0006_populate_recipe_slugs'),
        ('recipes', '0007_alter_recipe_image_alter_recipeimage_image'),
        ('recipes', '0008_alter_recipeimage_options_and_more'),
    ]
    
    with connection.cursor() as cursor:
        for app_label, migration_name in migrations_to_mark:
            # Verificar se a migração já está marcada
            cursor.execute("""
                SELECT COUNT(*) FROM django_migrations 
                WHERE app = %s AND name = %s;
            """, [app_label, migration_name])
            
            if cursor.fetchone()[0] == 0:
                print(f"Marcando migração {app_label}.{migration_name} como aplicada...")
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES (%s, %s, NOW());
                """, [app_label, migration_name])
            else:
                print(f"Migração {app_label}.{migration_name} já está marcada como aplicada.")

def main():
    """Função principal do script."""
    print("Iniciando correção de conflitos de migração...")
    
    try:
        with transaction.atomic():
            fix_recipeimage_table()
            mark_migrations_as_applied()
        
        print("\nCorreção concluída com sucesso!")
        print("Agora você pode executar 'python manage.py migrate' normalmente.")
        
    except Exception as e:
        print(f"Erro durante a correção: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()