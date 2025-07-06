# Generated manually to fix field rename conflict

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_recipeimage_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Verificar se existe uploaded_at e não existe created_at
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'recipes_recipeimage' AND column_name = 'uploaded_at')
                   AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name = 'recipes_recipeimage' AND column_name = 'created_at') THEN
                    -- Renomear uploaded_at para created_at
                    ALTER TABLE recipes_recipeimage RENAME COLUMN uploaded_at TO created_at;
                END IF;
                
                -- Se ambos existem, remover uploaded_at (dados duplicados)
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'recipes_recipeimage' AND column_name = 'uploaded_at')
                   AND EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'recipes_recipeimage' AND column_name = 'created_at') THEN
                    ALTER TABLE recipes_recipeimage DROP COLUMN uploaded_at;
                END IF;
                
                -- Garantir que updated_at existe
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'recipes_recipeimage' AND column_name = 'updated_at') THEN
                    ALTER TABLE recipes_recipeimage ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                END IF;
                
                -- Garantir que is_primary existe
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = 'recipes_recipeimage' AND column_name = 'is_primary') THEN
                    ALTER TABLE recipes_recipeimage ADD COLUMN is_primary BOOLEAN DEFAULT FALSE;
                END IF;
            END
            $$;
            """,
            reverse_sql="""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name = 'recipes_recipeimage' AND column_name = 'created_at') THEN
                    ALTER TABLE recipes_recipeimage RENAME COLUMN created_at TO uploaded_at;
                END IF;
            END
            $$;
            """
        ),
    ]