# Generated manually

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_add_is_primary_field'),
    ]

    operations = [
        # Adiciona o campo slug sem a restrição de unicidade
        migrations.AddField(
            model_name='recipe',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
        
        # Adiciona as outras alterações da migração original
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipe_images/', validators=[]),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='image',
            field=models.ImageField(upload_to='recipe_images/', validators=[]),
        ),
    ]