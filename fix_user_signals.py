#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from users.models import UserProfile

def check_signals_working():
    """Verifica se os signals do UserProfile estão funcionando"""
    print("🔍 VERIFICANDO SIGNALS DO USERPROFILE")
    print("=" * 40)
    
    # Criar um usuário de teste
    test_username = 'signal_test_user'
    
    # Remover usuário de teste se existir
    User.objects.filter(username=test_username).delete()
    
    try:
        # Criar usuário
        print(f"📝 Criando usuário de teste: {test_username}")
        test_user = User.objects.create_user(
            username=test_username,
            email='signal_test@example.com',
            password='testpass123'
        )
        
        # Verificar se o perfil foi criado automaticamente
        try:
            profile = UserProfile.objects.get(user=test_user)
            print("✅ Signal funcionando: Perfil criado automaticamente")
            signal_working = True
        except UserProfile.DoesNotExist:
            print("❌ Signal não funcionando: Perfil não foi criado")
            signal_working = False
        
        # Limpar dados de teste
        test_user.delete()
        
        return signal_working
        
    except Exception as e:
        print(f"❌ Erro ao testar signals: {e}")
        return False

def fix_existing_users_without_profiles():
    """Cria perfis para usuários que não têm"""
    print("\n🔧 CORRIGINDO USUÁRIOS SEM PERFIL")
    print("=" * 35)
    
    try:
        # Encontrar usuários sem perfil
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = users_without_profile.count()
        
        if count == 0:
            print("✅ Todos os usuários já têm perfil")
            return True
        
        print(f"📋 Encontrados {count} usuários sem perfil")
        
        # Criar perfis para usuários sem perfil
        created_count = 0
        for user in users_without_profile:
            try:
                UserProfile.objects.create(user=user)
                print(f"✅ Perfil criado para usuário: {user.username}")
                created_count += 1
            except Exception as e:
                print(f"❌ Erro ao criar perfil para {user.username}: {e}")
        
        print(f"\n📊 Resumo: {created_count}/{count} perfis criados")
        return created_count == count
        
    except Exception as e:
        print(f"❌ Erro ao corrigir usuários sem perfil: {e}")
        return False

def ensure_signals_are_connected():
    """Garante que os signals estão conectados"""
    print("\n🔗 VERIFICANDO CONEXÃO DOS SIGNALS")
    print("=" * 35)
    
    try:
        # Importar explicitamente os signals
        from users import signals
        print("✅ Módulo de signals importado")
        
        # Verificar se os signals estão registrados
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        
        # Listar receivers conectados ao signal post_save para User
        receivers = post_save._live_receivers(sender=User)
        
        print(f"📡 Encontrados {len(receivers)} receivers para User.post_save")
        
        # Verificar se nossos signals estão na lista
        signal_names = []
        for receiver in receivers:
            if hasattr(receiver, '__name__'):
                signal_names.append(receiver.__name__)
            elif hasattr(receiver, 'func') and hasattr(receiver.func, '__name__'):
                signal_names.append(receiver.func.__name__)
        
        print(f"📋 Receivers encontrados: {signal_names}")
        
        expected_signals = ['create_user_profile', 'save_user_profile']
        signals_connected = all(signal in str(signal_names) for signal in expected_signals)
        
        if signals_connected:
            print("✅ Signals do UserProfile estão conectados")
        else:
            print("⚠️ Alguns signals podem não estar conectados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar signals: {e}")
        return False

def test_profile_creation():
    """Testa a criação de perfil em tempo real"""
    print("\n🧪 TESTE DE CRIAÇÃO DE PERFIL")
    print("=" * 30)
    
    test_username = 'profile_creation_test'
    
    # Limpar usuário de teste se existir
    User.objects.filter(username=test_username).delete()
    
    try:
        print(f"👤 Criando usuário: {test_username}")
        
        # Criar usuário e verificar perfil imediatamente
        user = User.objects.create_user(
            username=test_username,
            email='profile_test@example.com',
            password='testpass123'
        )
        
        # Verificar se perfil existe
        try:
            profile = user.profile
            print(f"✅ Perfil encontrado: ID {profile.id}")
            print(f"📝 Descrição: '{profile.description}'")
            print(f"📅 Criado em: {profile.created_at}")
            success = True
        except UserProfile.DoesNotExist:
            print("❌ Perfil não encontrado")
            success = False
        
        # Limpar
        user.delete()
        
        return success
        
    except Exception as e:
        print(f"❌ Erro no teste de criação: {e}")
        return False

def main():
    print("🔧 DIAGNÓSTICO E CORREÇÃO DE SIGNALS DO USERPROFILE")
    print("=" * 60)
    
    # Verificar se signals estão conectados
    ensure_signals_are_connected()
    
    # Testar se signals funcionam
    signals_working = check_signals_working()
    
    # Corrigir usuários existentes sem perfil
    fix_existing_users_without_profiles()
    
    # Teste final de criação de perfil
    final_test = test_profile_creation()
    
    print("\n" + "=" * 60)
    if signals_working and final_test:
        print("🎉 SIGNALS DO USERPROFILE FUNCIONANDO CORRETAMENTE!")
        return True
    else:
        print("❌ PROBLEMAS DETECTADOS NOS SIGNALS")
        print("💡 Sugestões:")
        print("   - Verificar se users.apps.py está configurado corretamente")
        print("   - Verificar se signals.py está sendo importado")
        print("   - Verificar se o app 'users' está em INSTALLED_APPS")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)