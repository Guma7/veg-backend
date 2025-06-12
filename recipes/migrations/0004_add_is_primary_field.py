# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_add_recipeimage_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeimage',
            name='is_primary',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='recipeimage',
            name='image',
            field=models.ImageField(upload_to='recipe_images/', validators=[]),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipe_images/', validators=[]),
        ),
    ]