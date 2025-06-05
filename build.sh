#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔧 Instalando dependências..."
pip install -r requirements.txt

echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --no-input

echo "🔍 Verificando status do banco de dados..."
python check_db_status.py

echo "🔍 Verificando status das migrações antes..."
python manage.py showmigrations

echo "🚀 Executando correção de tabelas faltantes..."
python fix_missing_tables.py

echo "🔧 Corrigindo problemas específicos no esquema do banco de dados..."
python fix_db_schema.py

echo "🔧 Corrigindo signals do UserProfile..."
python fix_user_signals.py

echo "✅ Verificando status final do banco de dados..."
python check_db_status.py

echo "=== Build concluído com sucesso ==="