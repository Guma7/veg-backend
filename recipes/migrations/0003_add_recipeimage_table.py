# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_delete_recipetag_alter_recipe_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'recipes_recipeimage') THEN
                    CREATE TABLE recipes_recipeimage (
                        id BIGSERIAL PRIMARY KEY,
                        image VARCHAR(100) NOT NULL,
                        uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        recipe_id BIGINT NOT NULL REFERENCES recipes_recipe(id) ON DELETE CASCADE
                    );
                    CREATE INDEX recipes_recipeimage_recipe_id_idx ON recipes_recipeimage(recipe_id);
                END IF;
            END
            $$;
            """,
            reverse_sql="DROP TABLE IF EXISTS recipes_recipeimage;"
        ),
    ]