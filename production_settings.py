# Configurações específicas para produção no Render
# Este arquivo força configurações não-interativas para evitar problemas de deploy

from .backend.settings import *
import os

# Forçar modo não-interativo para migrações
DJANGO_SETTINGS_MODULE = 'backend.settings'

# Configurações específicas para migrações em produção
MIGRATION_MODULES = {
    'recipes': 'recipes.migrations',
    'users': 'users.migrations',
}

# Configurações para evitar prompts interativos
class NonInteractiveSettings:
    """Configurações para evitar prompts interativos durante deploy."""
    
    @staticmethod
    def setup():
        """Configura o ambiente para ser não-interativo."""
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
        
        # Monkey patch para questioner
        from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
        
        original_ask_rename = NonInteractiveMigrationQuestioner.ask_rename
        
        def auto_ask_rename(self, model_name, old_name, new_name, field_instance):
            # Automaticamente responder para renomeações conhecidas
            known_renames = {
                ('recipeimage', 'uploaded_at', 'created_at'): True,
            }
            
            key = (model_name.lower(), old_name, new_name)
            if key in known_renames:
                return known_renames[key]
            
            # Para outras renomeações, usar comportamento padrão não-interativo
            return False
        
        NonInteractiveMigrationQuestioner.ask_rename = auto_ask_rename

# Aplicar configurações automaticamente quando importado
NonInteractiveSettings.setup()

# Configurações de logging para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.db.migrations': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

print("Configurações de produção carregadas - Modo não-interativo ativado")