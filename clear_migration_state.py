#!/usr/bin/env python
"""
Script para limpar o estado das migrações e evitar conflitos de detecção automática.
Este script marca todas as migrações como aplicadas sem executá-las.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection, transaction
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.loader import MigrationLoader

def clear_migration_state():
    """Limpa o estado das migrações problemáticas."""
    print("Limpando estado das migrações...")
    
    with connection.cursor() as cursor:
        # Remover registros de migrações problemáticas
        problematic_migrations = [
            ('recipes', '0003_add_recipeimage_table'),
            ('recipes', '0004_add_is_primary_field'),
            ('recipes', '0008_alter_recipeimage_options_and_more'),
        ]
        
        for app_label, migration_name in problematic_migrations:
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = %s AND name = %s;
            """, [app_label, migration_name])
            print(f"Removido registro de migração: {app_label}.{migration_name}")

def mark_migrations_as_applied():
    """Marca todas as migrações como aplicadas."""
    print("Marcando migrações como aplicadas...")
    
    migrations_to_mark = [
        ('recipes', '0001_initial'),
        ('recipes', '0002_delete_recipetag_alter_recipe_options_and_more'),
        ('recipes', '0003_add_recipeimage_table'),
        ('recipes', '0004_add_is_primary_field'),
        ('recipes', '0005_add_recipe_slug_field'),
        ('recipes', '0006_populate_recipe_slugs'),
        ('recipes', '0007_alter_recipe_image_alter_recipeimage_image'),
        ('recipes', '0008_alter_recipeimage_options_and_more'),
        ('recipes', '0009_fix_field_rename_conflict'),
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

def ensure_table_structure():
    """Garante que a estrutura da tabela está correta."""
    print("Verificando estrutura da tabela recipes_recipeimage...")
    
    with connection.cursor() as cursor:
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'recipes_recipeimage'
            );
        """)
        
        if not cursor.fetchone()[0]:
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
            print("Tabela criada com sucesso.")
        else:
            print("Tabela já existe. Verificando colunas...")
            
            # Verificar e corrigir colunas
            columns_to_check = {
                'is_primary': 'BOOLEAN DEFAULT FALSE',
                'created_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
                'updated_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            }
            
            for column_name, column_def in columns_to_check.items():
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'recipes_recipeimage' AND column_name = %s
                    );
                """, [column_name])
                
                if not cursor.fetchone()[0]:
                    print(f"Adicionando coluna {column_name}...")
                    cursor.execute(f"ALTER TABLE recipes_recipeimage ADD COLUMN {column_name} {column_def};")
            
            # Verificar se uploaded_at existe e renomear para created_at
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'recipes_recipeimage' AND column_name = 'uploaded_at'
                );
            """)
            
            if cursor.fetchone()[0]:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'recipes_recipeimage' AND column_name = 'created_at'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    print("Renomeando uploaded_at para created_at...")
                    cursor.execute("ALTER TABLE recipes_recipeimage RENAME COLUMN uploaded_at TO created_at;")
                else:
                    print("Removendo coluna duplicada uploaded_at...")
                    cursor.execute("ALTER TABLE recipes_recipeimage DROP COLUMN uploaded_at;")

def main():
    """Função principal do script."""
    print("Iniciando limpeza do estado das migrações...")
    
    try:
        with transaction.atomic():
            ensure_table_structure()
            clear_migration_state()
            mark_migrations_as_applied()
        
        print("\nLimpeza concluída com sucesso!")
        print("Agora você pode executar 'python manage.py migrate' sem conflitos.")
        
    except Exception as e:
        print(f"Erro durante a limpeza: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()