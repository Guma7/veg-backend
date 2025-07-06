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

echo "🚀 Executando script de deploy com migrações seguras..."
python deploy_migrate.py

echo "🔍 Verificando status das migrações após deploy..."
python manage.py showmigrations

echo "✅ Verificando status final do banco de dados..."
python check_db_status.py

echo "=== Build concluído com sucesso ==="