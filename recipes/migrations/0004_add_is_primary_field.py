# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_add_recipeimage_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Adicionar campo is_primary se não existir
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'recipes_recipeimage' AND column_name = 'is_primary') THEN
                    ALTER TABLE recipes_recipeimage ADD COLUMN is_primary BOOLEAN DEFAULT FALSE;
                END IF;
                
                -- Adicionar campos created_at e updated_at se não existirem
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'recipes_recipeimage' AND column_name = 'created_at') THEN
                    ALTER TABLE recipes_recipeimage ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                END IF;
                
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'recipes_recipeimage' AND column_name = 'updated_at') THEN
                    ALTER TABLE recipes_recipeimage ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                END IF;
            END
            $$;
            """,
            reverse_sql="""
            ALTER TABLE recipes_recipeimage DROP COLUMN IF EXISTS is_primary;
            ALTER TABLE recipes_recipeimage DROP COLUMN IF EXISTS created_at;
            ALTER TABLE recipes_recipeimage DROP COLUMN IF EXISTS updated_at;
            """
        ),
    ]