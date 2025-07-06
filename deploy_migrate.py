#!/usr/bin/env python
"""
Script de migração para deploy no Render.
Este script executa migrações de forma não-interativa e segura.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Configurar o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Forçar modo não-interativo
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
os.environ['PYTHONUNBUFFERED'] = '1'

django.setup()

from django.db import connection, transaction
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.state import ProjectState
from django.db.migrations.loader import MigrationLoader
from django.apps import apps

def setup_non_interactive_mode():
    """Configura o Django para modo não-interativo."""
    # Monkey patch para forçar respostas automáticas
    original_ask_rename = NonInteractiveMigrationQuestioner.ask_rename
    
    def auto_ask_rename(self, model_name, old_name, new_name, field_instance):
        # Automaticamente responder 'sim' para renomeação de uploaded_at -> created_at
        if old_name == 'uploaded_at' and new_name == 'created_at':
            return True
        return original_ask_rename(self, model_name, old_name, new_name, field_instance)
    
    NonInteractiveMigrationQuestioner.ask_rename = auto_ask_rename
    print("Modo não-interativo configurado.")

def check_database_connection():
    """Verifica a conexão com o banco de dados."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("Conexão com banco de dados: OK")
        return True
    except Exception as e:
        print(f"Erro na conexão com banco de dados: {e}")
        return False

def ensure_migration_table():
    """Garante que a tabela django_migrations existe."""
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id SERIAL PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
    print("Tabela django_migrations verificada.")

def fix_recipeimage_structure():
    """Corrige a estrutura da tabela RecipeImage antes das migrações."""
    print("Verificando estrutura da tabela recipes_recipeimage...")
    
    with connection.cursor() as cursor:
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'recipes_recipeimage'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
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
                CREATE INDEX IF NOT EXISTS recipes_recipeimage_recipe_id_idx ON recipes_recipeimage(recipe_id);
            """)
            print("Tabela recipes_recipeimage criada.")
        else:
            print("Tabela recipes_recipeimage já existe. Verificando colunas...")
            
            # Verificar e corrigir uploaded_at -> created_at
            cursor.execute("""
                SELECT 
                    EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'recipes_recipeimage' AND column_name = 'uploaded_at') as has_uploaded_at,
                    EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'recipes_recipeimage' AND column_name = 'created_at') as has_created_at;
            """)
            
            has_uploaded_at, has_created_at = cursor.fetchone()
            
            if has_uploaded_at and not has_created_at:
                print("Renomeando uploaded_at para created_at...")
                cursor.execute("ALTER TABLE recipes_recipeimage RENAME COLUMN uploaded_at TO created_at;")
            elif has_uploaded_at and has_created_at:
                print("Removendo coluna duplicada uploaded_at...")
                cursor.execute("ALTER TABLE recipes_recipeimage DROP COLUMN uploaded_at;")
            
            # Verificar outras colunas necessárias
            required_columns = {
                'is_primary': 'BOOLEAN DEFAULT FALSE',
                'updated_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            }
            
            for column_name, column_def in required_columns.items():
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'recipes_recipeimage' AND column_name = %s
                    );
                """, [column_name])
                
                if not cursor.fetchone()[0]:
                    print(f"Adicionando coluna {column_name}...")
                    cursor.execute(f"ALTER TABLE recipes_recipeimage ADD COLUMN {column_name} {column_def};")

def run_migrations():
    """Executa as migrações de forma segura."""
    print("Executando migrações...")
    
    try:
        # Executar migrate com configurações não-interativas
        from django.core.management import call_command
        call_command('migrate', verbosity=2, interactive=False)
        print("Migrações executadas com sucesso.")
        return True
    except Exception as e:
        print(f"Erro durante as migrações: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal do script de deploy."""
    print("=== Script de Deploy - Migrações ===")
    print("Iniciando processo de migração para deploy...")
    
    try:
        # Verificar conexão
        if not check_database_connection():
            sys.exit(1)
        
        # Configurar modo não-interativo
        setup_non_interactive_mode()
        
        with transaction.atomic():
            # Garantir tabela de migrações
            ensure_migration_table()
            
            # Corrigir estrutura da tabela
            fix_recipeimage_structure()
        
        # Executar migrações
        if run_migrations():
            print("\n✅ Deploy de migrações concluído com sucesso!")
        else:
            print("\n❌ Falha no deploy de migrações.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Erro crítico durante o deploy: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()