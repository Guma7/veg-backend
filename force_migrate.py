#!/usr/bin/env python
"""
Script para forçar a aplicação de migrações no ambiente de produção.
Este script deve ser executado no servidor do Render.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection, transaction
from django.core.management.color import no_style
from django.db.migrations.executor import MigrationExecutor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def check_database_connection():
    """Verifica se a conexão com o banco de dados está funcionando"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✓ Conectado ao PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"✗ Erro na conexão com o banco de dados: {e}")
        return False

def create_migration_table():
    """Cria a tabela django_migrations se não existir"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_migrations (
                    id SERIAL PRIMARY KEY,
                    app VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied TIMESTAMP WITH TIME ZONE NOT NULL
                );
            """)
            print("✓ Tabela django_migrations verificada/criada")
            return True
    except Exception as e:
        print(f"✗ Erro ao criar tabela django_migrations: {e}")
        return False

def check_pending_migrations():
    """Verifica se há migrações pendentes"""
    try:
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"⚠️  Há {len(plan)} migrações pendentes:")
            for migration, backwards in plan:
                print(f"  - {migration.app_label}.{migration.name}")
            return True
        else:
            print("✓ Não há migrações pendentes")
            return False
    except Exception as e:
        print(f"✗ Erro ao verificar migrações pendentes: {e}")
        return False

def apply_migrations():
    """Aplica todas as migrações pendentes"""
    try:
        print("\n=== Aplicando migrações ===")
        
        # Primeiro, aplicar migrações do Django (auth, contenttypes, etc.)
        print("Aplicando migrações do Django...")
        execute_from_command_line(['manage.py', 'migrate', 'auth', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'contenttypes', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'sessions', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'admin', '--verbosity=2'])
        
        # Depois, aplicar migrações dos apps customizados
        print("\nAplicando migrações dos apps customizados...")
        execute_from_command_line(['manage.py', 'migrate', 'users', '--verbosity=2'])
        execute_from_command_line(['manage.py', 'migrate', 'recipes', '--verbosity=2'])
        
        # Finalmente, aplicar todas as migrações restantes
        print("\nAplicando todas as migrações restantes...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        
        print("✓ Todas as migrações foram aplicadas com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao aplicar migrações: {e}")
        return False

def verify_tables():
    """Verifica se as tabelas principais foram criadas"""
    try:
        with connection.cursor() as cursor:
            # Listar todas as tabelas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"\n✓ Tabelas criadas ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
            
            # Verificar tabelas específicas
            required_tables = ['auth_user', 'recipes_recipe', 'users_userprofile']
            missing_tables = []
            
            for table in required_tables:
                if table in tables:
                    print(f"✓ {table} existe")
                else:
                    print(f"✗ {table} NÃO existe")
                    missing_tables.append(table)
            
            # Verificar se o campo slug existe na tabela recipes_recipe
            if 'recipes_recipe' in tables:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = 'recipes_recipe'
                    ORDER BY column_name;
                """)
                columns = [row[0] for row in cursor.fetchall()]
                
                if 'slug' in columns:
                    print("✓ Campo 'slug' existe na tabela recipes_recipe")
                else:
                    print("✗ Campo 'slug' NÃO existe na tabela recipes_recipe")
                    missing_tables.append('recipes_recipe.slug')
            
            return len(missing_tables) == 0
            
    except Exception as e:
        print(f"✗ Erro ao verificar tabelas: {e}")
        return False

def main():
    print("=== Script de Migração Forçada ===")
    print("Este script irá aplicar todas as migrações necessárias.\n")
    
    # Verificar conexão
    if not check_database_connection():
        sys.exit(1)
    
    # Criar tabela de migrações se necessário
    if not create_migration_table():
        sys.exit(1)
    
    # Verificar migrações pendentes
    has_pending = check_pending_migrations()
    
    # Aplicar migrações
    if not apply_migrations():
        sys.exit(1)
    
    # Verificar se as tabelas foram criadas
    if not verify_tables():
        print("\n⚠️  Algumas tabelas ainda estão faltando. Pode ser necessário executar o script novamente.")
        sys.exit(1)
    
    print("\n✓ Todas as migrações foram aplicadas com sucesso!")
    print("✓ Todas as tabelas necessárias estão presentes.")
    print("\n=== Script concluído ===")

if __name__ == '__main__':
    main()