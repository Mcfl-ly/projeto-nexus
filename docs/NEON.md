# Neon conectado ao Nexus

O projeto existente está vinculado à organização org-old-salad-99105534, projeto delicate-hill-49926515, branch production. O arquivo neon.ts foi preservado; somente Postgres é utilizado. O login próprio do Nexus, React, FastAPI e MongoDB permanecem na arquitetura existente.

## Configuração local

- As skills neon e neon-postgres estão em .agents/skills. A skill neon foi conferida com https://neon.com/.well-known/agent-skills/neon/SKILL.md.
- O MCP está em .codex/config.toml, usa OAuth e está restrito ao projeto indicado na URL. Não contém API keys. Sua autenticação é separada do CLI e pode ser solicitada no primeiro uso.
- neon deploy terminou com sucesso e gravou as variáveis privadas em .env.local, ignorado pelo Git.
- A API lê .env.local da raiz, preservando variáveis já definidas no processo. DATABASE_URL é usada para tráfego da aplicação; DATABASE_URL_UNPOOLED para inicialização do esquema.
- O CLI foi instalado em uma pasta local de ferramentas do Codex. A autenticação também usa um diretório de configuração separado; não copie esses arquivos para o repositório.

## Esquema

A inicialização está versionada em api routes/scripts/setup_neon_database.py. Ela cria as três tabelas e os índices de unicidade somente em banco vazio, sem os INSERTs demonstrativos. Se já houver um esquema, preserva os dados e exige revisão das migrações quando faltam campos.

Execute a partir da raiz, com as dependências Python instaladas:

~~~powershell
& '.\api routes\.venv\Scripts\python.exe' '.\api routes\scripts\setup_neon_database.py'
npm run build
~~~

## Verificação realizada

- npm run build: passou, 50 módulos transformados.
- A aplicação foi iniciada via Uvicorn e serviu o React compilado em /perfil.
- Cadastro, login, perfil, listagem, favoritos, mudança de nome, senha, refresh e exclusão: retornaram HTTP 200 usando o PostgreSQL real.
- Os testes foram feitos primeiro numa branch isolada, depois em production. A branch temporária e os registros de teste foram removidos.
- Os dados do PostgreSQL local não foram importados. MongoDB e provedores externos não foram alterados nem fazem parte dessa validação de Postgres.

## Publicação

O banco está hospedado; a API e o frontend ainda precisam ser publicados no Render, conforme docs/DEPLOY.md. Configure DATABASE_URL nas variáveis privadas do Render. O arquivo .env.local nunca deve ser enviado ao GitHub ou incluído na imagem Docker.
