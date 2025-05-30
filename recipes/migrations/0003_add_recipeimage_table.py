# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_delete_recipetag_alter_recipe_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='recipe_images/', validators=[core.validators.validate_image])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='recipes.recipe')),
            ],
        ),
    ]