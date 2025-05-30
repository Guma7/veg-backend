# Script para excluir todas as receitas cadastradas no banco de dados
import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Importar o modelo Recipe após a configuração do Django
from recipes.models import Recipe

# Contar quantas receitas existem antes da exclusão
recipe_count = Recipe.objects.count()
print(f"Encontradas {recipe_count} receitas no banco de dados.")

# Excluir todas as receitas
if recipe_count > 0:
    Recipe.objects.all().delete()
    print("Todas as receitas foram excluídas com sucesso!")
else:
    print("Não há receitas para excluir.")

# Verificar se a exclusão foi bem-sucedida
remaining = Recipe.objects.count()
print(f"Receitas restantes: {remaining}")