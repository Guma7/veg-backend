# Deploy no Render com render.yaml

## Configuração do Deploy

Este projeto está configurado para deploy no Render usando o arquivo `render.yaml` que está na pasta `backend`. Este arquivo contém todas as configurações necessárias para o deploy do backend, frontend e banco de dados.

## Importante: Localização do render.yaml

O arquivo `render.yaml` deve estar **dentro da pasta backend** para que o Render possa lê-lo corretamente durante o deploy do backend. Isso é fundamental porque:

1. O Render lê apenas os arquivos dentro da pasta que está sendo implantada
2. Para o serviço backend, apenas os arquivos dentro da pasta `backend` são considerados
3. Para o serviço frontend, apenas os arquivos dentro da pasta `frontend` são considerados

## Como Funciona o Deploy

Quando você conecta seu repositório ao Render:

1. O Render detecta automaticamente o arquivo `render.yaml` na pasta backend
2. As configurações definidas neste arquivo são aplicadas aos serviços
3. Os comandos de build e start são executados conforme especificado

## Migrações do Banco de Dados

O processo de deploy inclui a execução de scripts especiais para garantir que todas as migrações sejam aplicadas corretamente:

1. `check_db_status.py`: Verifica o status do banco de dados
2. `fix_missing_tables.py`: Corrige tabelas faltantes
3. `fix_db_schema.py`: Corrige especificamente a tabela `users_userprofile` e a coluna `slug`
4. `fix_user_signals.py`: Corrige problemas com os signals do Django

Estes scripts são executados na ordem correta para garantir que o banco de dados esteja configurado adequadamente antes de iniciar a aplicação.

## Configuração do Banco de Dados

O banco de dados PostgreSQL é configurado no plano gratuito do Render. As credenciais e a URL de conexão são gerenciadas automaticamente pelo Render e injetadas como variáveis de ambiente no serviço backend.

## Variáveis de Ambiente

Todas as variáveis de ambiente necessárias estão definidas no arquivo `render.yaml`, incluindo:

- Configurações do Python e do servidor web
- Configurações do Django (SECRET_KEY, DEBUG, etc.)
- Configurações de CORS e CSRF
- URL da API para o frontend

## Como Fazer o Deploy

Para fazer o deploy no plano gratuito do Render:

1. Faça login no [Render](https://dashboard.render.com/)
2. Crie um novo serviço Web para o backend:
   - Conecte seu repositório GitHub/GitLab/Bitbucket
   - Selecione a pasta `backend` como diretório raiz
   - O Render detectará automaticamente o arquivo `render.yaml`

3. Crie um novo serviço Web para o frontend:
   - Conecte o mesmo repositório
   - Selecione a pasta `frontend` como diretório raiz

4. Crie um banco de dados PostgreSQL no plano gratuito

5. Conecte os serviços ao banco de dados usando a variável de ambiente `DATABASE_URL`

## Verificação do Deploy

Após o deploy, verifique se os problemas foram resolvidos:

1. Tente registrar um novo usuário no site
2. Verifique se as receitas em destaque estão sendo exibidas corretamente
3. Verifique os logs do serviço no Render para confirmar que não há mais erros

## Solução de Problemas

Se ainda houver problemas após o deploy:

1. Verifique os logs do serviço no Render para identificar erros específicos
2. Execute manualmente os scripts de correção através do console do Render:
   ```
   python fix_db_schema.py
   ```
3. Verifique se as variáveis de ambiente estão configuradas corretamente