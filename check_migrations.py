#!/usr/bin/env python
import os
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.commands.migrate import Command as MigrateCommand
from django.core.management.commands.showmigrations import Command as ShowMigrationsCommand

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def check_database_connection():
    """Verifica se a conexão com o banco de dados está funcionando"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Conexão com o banco de dados estabelecida com sucesso")
            return True
    except Exception as e:
        print(f"✗ Erro na conexão com o banco de dados: {e}")
        return False

def check_tables_exist():
    """Verifica se as tabelas principais existem"""
    try:
        with connection.cursor() as cursor:
            # Verificar se a tabela auth_user existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user'
                );
            """)
            auth_user_exists = cursor.fetchone()[0]
            
            # Verificar se a tabela recipes_recipe existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'recipes_recipe'
                );
            """)
            recipes_recipe_exists = cursor.fetchone()[0]
            
            # Verificar se o campo slug existe na tabela recipes_recipe
            slug_exists = False
            if recipes_recipe_exists:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'recipes_recipe'
                        AND column_name = 'slug'
                    );
                """)
                slug_exists = cursor.fetchone()[0]
            
            print(f"✓ Tabela auth_user existe: {auth_user_exists}")
            print(f"✓ Tabela recipes_recipe existe: {recipes_recipe_exists}")
            print(f"✓ Campo slug na recipes_recipe existe: {slug_exists}")
            
            return auth_user_exists and recipes_recipe_exists and slug_exists
            
    except Exception as e:
        print(f"✗ Erro ao verificar tabelas: {e}")
        return False

def show_migration_status():
    """Mostra o status das migrações"""
    try:
        print("\n=== Status das Migrações ===")
        execute_from_command_line(['manage.py', 'showmigrations'])
        return True
    except Exception as e:
        print(f"✗ Erro ao mostrar status das migrações: {e}")
        return False

def apply_migrations():
    """Aplica as migrações pendentes"""
    try:
        print("\n=== Aplicando Migrações ===")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✓ Migrações aplicadas com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao aplicar migrações: {e}")
        return False

if __name__ == '__main__':
    print("=== Verificação do Banco de Dados e Migrações ===")
    
    # Verificar conexão
    if not check_database_connection():
        exit(1)
    
    # Mostrar status das migrações
    show_migration_status()
    
    # Verificar se as tabelas existem
    tables_ok = check_tables_exist()
    
    if not tables_ok:
        print("\n⚠️  Algumas tabelas ou campos estão faltando. Aplicando migrações...")
        if apply_migrations():
            print("\n=== Verificação Final ===")
            check_tables_exist()
        else:
            print("\n✗ Falha ao aplicar migrações")
            exit(1)
    else:
        print("\n✓ Todas as tabelas e campos necessários estão presentes")
    
    print("\n=== Verificação Concluída ===")