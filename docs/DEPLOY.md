# Publicar o Nexus sem contratar planos pagos

A configuração usa um único Web Service **Free** no Render para servir React e FastAPI no mesmo endereço HTTPS, PostgreSQL no plano **Free** do Neon e MongoDB no Atlas. Dessa forma, os cookies não dependem de domínios diferentes. O `render.yaml` não cria bancos pagos.

## 1. Criar as contas

- Render: https://dashboard.render.com — entrar com o GitHub e autorizar o repositório do Nexus.
- Neon: https://console.neon.tech — criar um projeto no plano Free, de preferência em região próxima à escolhida no Render.
- Atlas: usar sua conta existente; confirmar que o cluster escolhido está no plano gratuito.

O Render Free suspende a aplicação após 15 minutos sem tráfego; o primeiro acesso seguinte pode demorar. Neon e Atlas também têm cotas. Consulte os painéis e mantenha os planos gratuitos selecionados. O PostgreSQL Free do Render expira em 30 dias e não faz parte desta configuração.

## 2. Preparar o PostgreSQL no Neon

Crie o projeto e abra **Connect**. Guarde a connection string com SSL nas configurações privadas do Render como `DATABASE_URL`. Não a coloque em commits, mensagens ou variáveis `VITE_*`.

Para começar com um banco vazio, no SQL Editor do Neon execute somente os três `CREATE TABLE` iniciais de `originais/sql_proj.psql` e o `CREATE UNIQUE INDEX users_login_lower_unique` desse arquivo. Não execute os INSERTs de demonstração. Depois execute `api routes/migrations/002_library_uniqueness.sql`.

O esquema novo já possui `login` e `favorite`. Se estiver restaurando um banco antigo, aplique em ordem as migrações 001 (em `originais/migrations`) e 002, 003 e 004 (em `api routes/migrations`), conforme necessário. A aplicação não executa migrações automaticamente.

Se quiser manter usuários e conteúdos locais, faça a transferência antes de usar o banco público: exporte/restaure PostgreSQL e MongoDB preservando os ObjectIds do catálogo. Não restaure dados por cima de um banco com usuários ativos. Não transfira somente o PostgreSQL: seus registros referenciam documentos do MongoDB.

## 3. Preparar o Atlas

Em **Database Access**, crie um usuário para a aplicação com acesso somente ao banco necessário. Em **Connect → Drivers**, obtenha a URI e salve como `CONNECTION_STRING` no Render. Configure também `DATABASE` e `COLECAO` com os nomes reais do banco e coleção.

Em **Network Access**, permita as faixas de IP de saída exibidas pelo serviço do Render. Não é necessário deixar o acesso aberto a todos os IPs. Se o Atlas já contém seu catálogo, preserve o banco, a coleção e seus identificadores.

## 4. Enviar as alterações ao GitHub

Revise `git status` e o diff no seu editor. O `.gitignore` exclui ambientes locais, segredos, caches e exports do banco. Os caches que já estavam versionados foram retirados apenas do índice Git; os arquivos locais foram preservados.

Envie o Dockerfile, render.yaml, arquivos de configuração, código, migrações e exemplos `.env.example`. Não envie seu `.env` real nem backups. Faça commit e push pelo fluxo habitual do seu editor.

## 5. Criar o serviço no Render

No dashboard do Render, selecione **New → Blueprint**, escolha o repositório e a branch com as alterações. Use o `render.yaml` da raiz e confira que há apenas um Web Service no plano Free. A raiz do build é a raiz do repositório, não `api routes`.

Preencha as variáveis privadas solicitadas:

| Variável | Valor |
| --- | --- |
| `DATABASE_URL` | Connection string do Neon com SSL |
| `CONNECTION_STRING` | URI do MongoDB Atlas |
| `DATABASE` | Nome do banco MongoDB |
| `COLECAO` | Nome da coleção |
| `TMDB_KEY` | Chave da integração de filmes |
| `TWITCH_CLIENT_ID` | Client ID da integração de jogos |
| `TWITCH_CLIENT_SECRET` | Client secret da integração de jogos |

O Blueprint gera `SECRET_KEY` e configura `APP_ENV=production`, `ALGORITHM=HS256`, `COOKIE_SECURE=true` e `COOKIE_SAMESITE=lax`. Não configure `PORT` para o banco: o Render reserva essa variável para a aplicação HTTP. A API usa `DATABASE_URL`; localmente, `DB_PORT` pode substituir o antigo `PORT`.

O Dockerfile compila o React e copia o resultado para a imagem da API. Não configure `VITE_API_URL` para esse deploy: o frontend usa o mesmo endereço da página. O `.dockerignore` impede a cópia de `.env`, ambientes virtuais e backups para a imagem.

## 6. Conferir o primeiro deploy

Acompanhe os logs do build e do serviço. Depois abra:

- `https://SEU-SERVICO.onrender.com/health` — deve retornar `{"status":"ok"}`. Esse endpoint verifica a aplicação, não a disponibilidade dos bancos.
- `/cadastro` — criar uma conta de teste com login comum.
- `/login` — entrar, atualizar a página e verificar a sessão.
- Adicionar um filme, um jogo e um livro; testar o cadastro manual.
- Favoritar e desmarcar; conferir a Home.
- `/perfil` — mudar nome e senha e conferir a quantidade de conteúdos.
- Sair e entrar novamente com a senha nova.
- Abrir diretamente e atualizar `/perfil` e `/filmes` para conferir as rotas do React.

Não considere o deploy concluído até validar esses fluxos com os bancos hospedados. O build do container precisa ser validado no Render ou em uma máquina com Docker.

## 7. Operação inicial

Monitore cotas e erros pelos painéis dos provedores. Faça exports periódicos dos dois bancos e teste restauração; não dependa de uma política de backup paga sem conferir o plano. Não grave dados persistentes no disco do Render Free.

As rotas continuam usando chamadas síncronas a banco e provedores dentro de funções assíncronas; esta configuração inicial precisa de teste de carga antes de ser usada para tráfego maior. A renovação automática da sessão no frontend e proteção contra excesso de tentativas de login continuam como próximos ajustes.

Referências: [Render Free](https://render.com/docs/free), [Render Blueprint](https://render.com/docs/blueprint-spec), [Neon Free](https://neon.com/pricing), [Atlas Free](https://www.mongodb.com/docs/atlas/reference/free-shared-limitations/).
