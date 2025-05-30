# Generated manually

from django.db import migrations, models
from django.utils.text import slugify
import uuid
import core.validators
import recipes.models

def generate_unique_slug(title):
    # Cria um slug base a partir do título
    # Se o título for vazio ou None, usa 'receita' como base
    if not title:
        title = 'receita'
    slug = slugify(title)
    # Adiciona um UUID curto para garantir unicidade
    unique_id = str(uuid.uuid4())[:8]
    return f"{slug}-{unique_id}"

def populate_recipe_slugs(apps, schema_editor):
    # Obtém o modelo Recipe do estado atual das migrações
    Recipe = apps.get_model('recipes', 'Recipe')
    
    # Para cada receita, gera um slug único
    # Importante: processa TODAS as receitas, não apenas as sem slug
    for recipe in Recipe.objects.all():
        # Garante que todas as receitas tenham um slug, mesmo que já exista um
        recipe.slug = generate_unique_slug(recipe.title)
        recipe.save()

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_add_recipe_slug_field'),
    ]

    operations = [
        # Executa a função para preencher os slugs
        migrations.RunPython(populate_recipe_slugs),
        
        # Altera o campo slug para adicionar a restrição de unicidade
        migrations.AlterField(
            model_name='recipe',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]