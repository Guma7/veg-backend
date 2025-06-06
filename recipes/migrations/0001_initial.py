# Generated by Django 5.2 on 2025-04-29 00:17

import core.validators
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('usage_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-usage_count'],
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RatingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rating', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='recipes.rating')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(3)])),
                ('genre', models.CharField(choices=[('ENTRADA', 'Entrada'), ('PRINCIPAL', 'Prato Principal'), ('SOBREMESA', 'Sobremesa')], default='ENTRADA', max_length=50)),
                ('recipe_class', models.CharField(choices=[('ENTRADA', 'Entrada'), ('PRATO_PRINCIPAL', 'Prato Principal'), ('SOBREMESA', 'Sobremesa'), ('LANCHE', 'Lanche'), ('QUEIJOS_VEGANOS', 'Queijos Veganos'), ('FRIOS_VEGANOS', 'Frios Veganos'), ('CARNES_VEGANAS', 'Carnes Veganas'), ('ANIVERSARIO_VEGANO', 'Aniversário Vegano'), ('SUCO', 'Suco'), ('DRINK', 'Drink')], max_length=50)),
                ('style', models.CharField(choices=[('GOURMET', 'Gourmet'), ('CASEIRA', 'Caseira')], default='CASEIRA', max_length=50)),
                ('nutritional_level', models.CharField(blank=True, choices=[('BAIXO', 'Baixo'), ('MEDIO', 'Médio'), ('ALTO', 'Alto')], max_length=50, null=True)),
                ('does_not_contain', models.CharField(blank=True, max_length=200, null=True)),
                ('traditional', models.CharField(blank=True, max_length=200, null=True)),
                ('ingredients', models.TextField()),
                ('instructions', models.TextField()),
                ('youtube_link', models.URLField(blank=True, null=True, validators=[core.validators.validate_youtube_link])),
                ('image', models.ImageField(upload_to='recipe_images/', validators=[core.validators.validate_image])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('views_count', models.IntegerField(default=0)),
                ('is_featured', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='rating',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='recipes.recipe'),
        ),
        migrations.CreateModel(
            name='RecipeImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='recipe_images/', validators=[core.validators.validate_image])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='recipes.recipe')),
            ],
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['recipe_class'], name='recipes_rec_recipe__2d0411_idx'),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['style'], name='recipes_rec_style_a1a936_idx'),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['genre'], name='recipes_rec_genre_7f1fba_idx'),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['nutritional_level'], name='recipes_rec_nutriti_752f59_idx'),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['traditional'], name='recipes_rec_traditi_05963a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together={('recipe', 'user')},
        ),
    ]
