#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Instalando dependências ==="
pip install -r requirements.txt

echo "=== Verificando status das migrações ==="
python manage.py showmigrations

echo "=== Coletando arquivos estáticos ==="
python manage.py collectstatic --no-input

echo "=== Executando script de migração forçada ==="
python force_migrate.py

echo "=== Verificação final das migrações ==="
python manage.py showmigrations

echo "=== Build concluído com sucesso ==="