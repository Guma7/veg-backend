# Guia de Solução de Problemas - Deploy no Render

## Problemas Identificados e Soluções

### 1. Erro "relation 'auth_user' does not exist"

**Problema**: As migrações do Django não estão sendo aplicadas corretamente no banco de dados PostgreSQL do Render.

**Causa**: O banco de dados está vazio e as migrações não foram executadas durante o deploy.

**Solução**: 
- Modificamos o `build.sh` para incluir um script de migração forçada
- Criamos o script `force_migrate.py` que aplica as migrações de forma sequencial
- O script verifica a conexão com o banco e aplica as migrações em ordem específica

### 2. Erro "column recipes_recipe.slug does not exist"

**Problema**: O campo `slug` não existe na tabela `recipes_recipe`.

**Causa**: A migração que adiciona o campo `slug` não foi aplicada.

**Solução**:
- Verificamos que as migrações `0005_add_recipe_slug_field.py` e `0006_populate_recipe_slugs.py` existem
- O script `force_migrate.py` garante que essas migrações sejam aplicadas

### 3. Erros de Validação de Senha

**Problema**: Senhas com menos de 8 caracteres estão sendo rejeitadas.

**Causa**: O Django tem validadores de senha padrão que exigem pelo menos 8 caracteres.

**Solução**:
- Configuramos explicitamente o `MinimumLengthValidator` com 8 caracteres
- O frontend deve garantir que as senhas tenham pelo menos 8 caracteres

## Arquivos Modificados

### 1. `build.sh`
```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Instalando dependências ==="
pip install -r requirements.txt

echo "=== Verificando status das migrações ==="
python manage.py showmigrations

echo "=== Coletando arquivos estáticos ==="
python manage.py collectstatic --no-input

echo "=== Executando script de migração forçada ==="
python force_migrate.py

echo "=== Verificação final das migrações ==="
python manage.py showmigrations

echo "=== Build concluído com sucesso ==="
```

### 2. `force_migrate.py` (Novo)
Script que:
- Verifica a conexão com o banco de dados
- Cria a tabela `django_migrations` se necessário
- Aplica migrações em ordem específica (Django core primeiro, depois apps customizados)
- Verifica se as tabelas foram criadas corretamente
- Confirma a existência do campo `slug` na tabela `recipes_recipe`

### 3. `settings.py`
Configurações atualizadas:
- `DEBUG = False` (sempre em produção)
- Configurações de CORS simplificadas
- Validadores de senha explícitos
- Configuração de banco de dados usando sempre a URL do Render

### 4. `wsgi.py`
Adicionado carregamento de variáveis de ambiente do arquivo `.env`

### 5. `requirements.txt`
Adicionado `python-dotenv==1.0.1`

## Como Verificar se o Deploy Funcionou

### 1. Logs do Build
Verifique os logs do build no Render para:
- ✅ "=== Instalando dependências ==="
- ✅ "=== Verificando status das migrações ==="
- ✅ "=== Executando script de migração forçada ==="
- ✅ "✓ Conectado ao PostgreSQL"
- ✅ "✓ Todas as migrações foram aplicadas com sucesso"
- ✅ "✓ Tabela auth_user existe"
- ✅ "✓ Tabela recipes_recipe existe"
- ✅ "✓ Campo 'slug' existe na tabela recipes_recipe"

### 2. Logs da Aplicação
Verifique se não há mais erros como:
- ❌ "relation 'auth_user' does not exist"
- ❌ "column recipes_recipe.slug does not exist"

### 3. Funcionalidades do Frontend
Teste:
- ✅ Obtenção de token CSRF
- ✅ Registro de usuário (com senha de 8+ caracteres)
- ✅ Login de usuário
- ✅ Carregamento de receitas em destaque

## Próximos Passos

1. **Fazer um novo deploy** no Render para aplicar todas as mudanças
2. **Monitorar os logs** durante o build para confirmar que as migrações foram aplicadas
3. **Testar o frontend** para verificar se os erros foram resolvidos
4. **Verificar se o banco de dados** tem todas as tabelas necessárias

## Comandos Úteis para Debug

### No ambiente local (para teste):
```bash
# Verificar status das migrações
python manage.py showmigrations

# Aplicar migrações
python manage.py migrate

# Testar validações
python test_validation.py
```

### No Render (via logs):
- Os logs do build mostrarão a execução do `force_migrate.py`
- Os logs da aplicação mostrarão se há erros de banco de dados

## Variáveis de Ambiente Necessárias no Render

```
DEBUG=False
DJANGO_SECRET_KEY=sua_chave_secreta
DATABASE_URL=postgresql://usuario:senha@host/database
ALLOWED_HOSTS=seu-app.onrender.com,localhost
CORS_ALLOWED_ORIGINS=https://seu-frontend.onrender.com
```

## Troubleshooting Adicional

### Se ainda houver problemas:

1. **Verificar logs detalhados** do Render
2. **Confirmar variáveis de ambiente** estão configuradas corretamente
3. **Verificar se o banco PostgreSQL** está acessível
4. **Testar conexão manual** com o banco (se possível)

### Comandos de emergência:

Se precisar resetar o banco de dados:
```bash
# CUIDADO: Isso apaga todos os dados!
python manage.py flush
python manage.py migrate
```

Se precisar recriar migrações:
```bash
python manage.py makemigrations
python manage.py migrate
```