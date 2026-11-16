# Nexus

**Biblioteca pessoal de filmes, jogos e livros, com foco em desenvolvimento backend Python.**

**Aplicação publicada:** [Acessar o Nexus](https://projeto-nexus-617m.onrender.com)

React e FastAPI são servidos pelo mesmo serviço no Render Free, com PostgreSQL no Neon e MongoDB Atlas. O primeiro acesso após inatividade pode demorar enquanto a instância gratuita inicia.

O Nexus é um projeto pessoal de portfólio para organizar conteúdos em um só lugar. A API permite manter uma biblioteca individual, acompanhar o status de cada item e registrar avaliações, integrando informações de três serviços externos.

O projeto reúne autenticação com JWT, controle de acesso por usuário, persistência em PostgreSQL e MongoDB e testes automatizados. A interface web em React permite cadastrar contas, entrar, gerenciar conteúdos, marcar favoritos e editar o perfil. Algumas áreas do dashboard ainda estão em desenvolvimento.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Autenticação | PyJWT, Argon2, cookies HttpOnly |
| Persistência | PostgreSQL com psycopg2; MongoDB com PyMongo |
| Integrações | Requests, TMDB, IGDB e Open Library |
| Frontend | React, JavaScript/JSX, React Router, CSS e Vite |
| Testes | Pytest, FastAPI TestClient e simulação de dependências |
| Hospedagem | Docker, Render Free, Neon PostgreSQL e MongoDB Atlas |

## Funcionalidades

### Usuários e autenticação

- Cadastro com nome de exibição, login e senha, sem exigir e-mail.
- Entrada por login e senha, com validação de dados.
- Hash de senhas com Argon2.
- Access token JWT com duração de 15 minutos.
- Refresh token JWT com duração de 30 dias, armazenado como hash no PostgreSQL.
- Rotação de refresh tokens e revogação no logout.
- Armazenamento dos tokens no navegador por cookies HttpOnly.
- Consulta de perfil, alteração de nome e senha e exclusão da conta.

### Login de acesso

O cadastro e a entrada usam `login` e senha. Novos logins aceitam de 3 a 50 letras, números, pontos, hífens e sublinhados, sem espaços; maiúsculas e minúsculas são equivalentes. O nome de exibição continua separado.

Não há envio ou verificação de e-mail. Em bancos migrados da versão anterior, o identificador antigo é preservado como login; o procedimento está na seção de migrações.

### Biblioteca pessoal

- Adição, listagem e remoção de filmes, jogos e livros.
- Adição por título consultando o primeiro resultado do provedor externo.
- Cadastro manual de conteúdos em janelas flutuantes específicas para filmes, jogos e livros.
- Campos manuais para título, data, gêneros, URL da capa e direção/autores quando aplicável.
- Registro de status e avaliação pela API; a interface permite alterar o status, mas a edição de avaliações ainda está pendente.
- Atualização parcial com PATCH, preservando os campos não enviados.
- Consultas e alterações da biblioteca vinculadas ao usuário autenticado.
- Favoritos persistidos por usuário, com botão de coração para marcar e desmarcar.

### Interface web

- Páginas de filmes, jogos e livros com listagem, mudança de status e exclusão.
- Botões de adicionar que abrem janelas com busca por título e cadastro manual.
- Home com conteúdos da biblioteca e seção “Seus favoritos”.
- Favoritos com até seis cards visíveis e rolagem vertical para acessar os demais.
- Página “Meu perfil” (`/perfil`) com alteração de nome de exibição, alteração de senha com confirmação e contagem total dos conteúdos adicionados.
- Layout adaptável ao celular e mensagens de sucesso e erro.

A alteração de nome no perfil modifica o nome de exibição, mantendo o login de acesso. A exclusão de conta existe na API, mas não está disponível nessa página.

### Integrações externas

| Conteúdo | Serviço | Dados utilizados |
| --- | --- | --- |
| Filmes | TMDB | Títulos, sinopse, lançamento, gêneros e pôster |
| Jogos | IGDB | Nome, lançamento, gêneros e capa |
| Livros | Open Library | Informações bibliográficas e capa, conforme disponibilidade |

O backend normaliza títulos e trata respostas inválidas, indisponibilidade e tempo limite das consultas externas. Os conteúdos obtidos são vinculados ao catálogo no MongoDB e à biblioteca do usuário no PostgreSQL.

## Arquitetura

```text
Navegador
    | HTTPS + cookies HttpOnly
    v
Render Free — container Docker
    React (arquivos estáticos) + FastAPI
                    |
          +---------+----------+
          |                    |
  PostgreSQL / Neon      MongoDB Atlas
  - usuários             - catálogo
  - refresh tokens       - metadados
  - biblioteca
  - favoritos

FastAPI também consulta TMDB, IGDB e Open Library.
```

O PostgreSQL armazena os dados relacionais dos usuários e suas bibliotecas. O MongoDB armazena documentos de catálogo com campos que variam conforme o tipo de conteúdo e o provedor. A biblioteca referencia o identificador do documento de catálogo.

As rotas estão separadas em módulos de autenticação, usuários e biblioteca. A validação de entrada utiliza Pydantic. A configuração de ambiente está em `api routes/settings.py`; as conexões PostgreSQL são abertas por requisição e encerradas ao final por `api routes/database.py`. O tratamento compartilhado de erros está em `routers/db_errors.py`.

## Estado atual

| Área | Situação |
| --- | --- |
| API de autenticação, usuários e biblioteca | Implementada |
| Integrações com os três provedores | Implementadas |
| Persistência em PostgreSQL e MongoDB | Implementada |
| Testes automatizados e integração com PostgreSQL | 187 testes aprovados na validação de 16/11/2026 |
| Frontend | Cadastro e entrada por login, sessão protegida, biblioteca, janelas de adição e perfil integrados |
| Dashboard | Biblioteca e favoritos integrados; seção de recentes ainda vazia e “Acompanhando agora” sem filtro por status |
| Docker e deploy | Aplicação publicada no Render Free; atualização por deploy manual |
| Bancos hospedados | Neon PostgreSQL e MongoDB Atlas conectados |
| Dependências | Revisadas em 16/11/2026; sem avisos conhecidos nas consultas realizadas |
| Redis e CI/CD | Planejados |

O frontend utiliza **JavaScript/JSX**. O projeto está publicado, com melhorias de sessão, qualidade e operação listadas nas próximas etapas.

## Estrutura do projeto

```text
.
├── api routes/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── settings.py
│   ├── database.py
│   ├── scripts/setup_neon_database.py
│   ├── migrations/
│   │   ├── 002_library_uniqueness.sql
│   │   ├── 003_library_favorites.sql
│   │   └── 004_users_login.sql
│   ├── routers/
│   │   ├── auth/routes.py
│   │   ├── library/routes.py
│   │   ├── users/routes.py
│   │   └── db_errors.py
│   └── tests/
├── front/nexus/
│   ├── package.json
│   └── src/
│       ├── Components/
│       ├── hooks/useLibrary.js
│       ├── home_page/
│       ├── movies_page/
│       ├── games_page/
│       ├── books_page/
│       ├── login_page/
│       ├── register_page/
│       └── profile_page/
├── originais/
│   ├── sql_proj.psql
│   └── migrations/001_library_columns.sql
├── docs/
│   ├── DEPLOY.md
│   ├── NEON.md
│   └── DEPENDENCIAS.md
├── modelos/
├── Dockerfile
├── render.yaml
├── neon.ts
├── package.json
└── README.md
```

## Executar localmente

### Pré-requisitos

- Python com suporte às dependências de `api routes/requirements.txt`.
- Node.js e npm compatíveis com a versão do Vite declarada em `front/nexus/package.json`.
- PostgreSQL e MongoDB acessíveis localmente ou por conexão remota.
- Credenciais TMDB e Twitch/IGDB para as respectivas integrações. A consulta atual à Open Library não utiliza chave de API.

Os comandos abaixo usam PowerShell. Comece na raiz do repositório. O ambiente usado na validação tinha Python 3.15 e Node.js 24.

### 1. Preparar o backend

```powershell
cd "api routes"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Configurar as variáveis de ambiente

Para uma configuração nova, copie `api routes/.env.example` para `api routes/.env` e preencha os valores. O exemplo abaixo usa bancos locais:

```dotenv
APP_ENV=development
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
CORS_ORIGINS=http://localhost:5173

# PostgreSQL
DBNAME=nexus
HOST=localhost
DB_PORT=5432
USER=postgres
PASSWORD=substitua_pela_senha_local

# JWT
SECRET_KEY=substitua_por_uma_chave_aleatoria_longa
ALGORITHM=HS256

# MongoDB
CONNECTION_STRING=mongodb://localhost:27017/
DATABASE=nexus
COLECAO=contents

# Provedores externos
TMDB_KEY=substitua_pela_chave_tmdb
TWITCH_CLIENT_ID=substitua_pelo_client_id
TWITCH_CLIENT_SECRET=substitua_pelo_client_secret
```

Para gerar uma chave JWT local:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Mantenha os arquivos de ambiente fora do versionamento. Os valores acima são exemplos. Para usar PostgreSQL hospedado, configure `DATABASE_URL` com SSL no lugar dos campos individuais. Use `DATABASE_URL_UNPOOLED` para inicialização e migrações no Neon.

A precedência da configuração é: variáveis já definidas no processo → `.env.local` da raiz → `.env` da raiz → `api routes/.env`. Assim, uma URL puxada pelo CLI do Neon na raiz prevalece sobre a configuração local do banco. Não coloque credenciais em variáveis `VITE_*`, pois elas são expostas ao navegador.

### 3. Preparar o PostgreSQL

Crie o banco informado em `DBNAME`. Para um banco novo, execute os três comandos `CREATE TABLE` iniciais de [originais/sql_proj.psql](originais/sql_proj.psql), que definem `users`, `refreshToken` e `userLibrary`. O esquema atual já contém `users.login` e `userlibrary.favorite`.

Execute também o `CREATE UNIQUE INDEX users_login_lower_unique` desse script, que impede logins duplicados com diferenças de maiúsculas e minúsculas. Os `INSERT`s demonstrativos seguintes usam senhas e tokens fictícios e não devem ser usados para criar contas reais.

#### Migrações e bancos existentes

As migrações são executadas manualmente; a API não as aplica ao iniciar. Pare a API e encerre transações abertas antes de alterar as tabelas, para evitar bloqueios. Execute os arquivos na ordem abaixo, conforme o estado do banco:

| Arquivo | Finalidade |
| --- | --- |
| [001_library_columns.sql](originais/migrations/001_library_columns.sql) | Adicionar `external_api_id` e `content_type` a bancos antigos |
| [002_library_uniqueness.sql](api%20routes/migrations/002_library_uniqueness.sql) | Criar índices de unicidade da biblioteca; duplicados existentes precisam ser revisados antes |
| [003_library_favorites.sql](api%20routes/migrations/003_library_favorites.sql) | Adicionar `favorite BOOLEAN NOT NULL DEFAULT FALSE` sem alterar os conteúdos existentes |
| [004_users_login.sql](api%20routes/migrations/004_users_login.sql) | Renomear `users.email` para `users.login`, preservando os valores, e garantir unicidade sem distinguir maiúsculas de minúsculas |

Para bancos novos, aplique também a migração 002 após criar o esquema. As migrações 003 e 004 podem ser repetidas no esquema atual. A migração 004 usa um tempo limite para bloqueios e pode falhar se houver transações abertas; nesse caso, encerre essas transações e tente novamente. Logins antigos conflitantes ao ignorar maiúsculas e minúsculas também precisam ser resolvidos antes de criar o índice.

Reinicie a API após atualizar o esquema. Contas anteriores continuam acessíveis usando seu identificador antigo no campo Login; novas contas usam um nome de login comum.

Para inicializar um banco vazio no Neon, com `DATABASE_URL_UNPOOLED` configurada na raiz e as dependências Python instaladas, execute a partir da raiz:

```powershell
& ".\api routes\.venv\Scripts\python.exe" ".\api routes\scripts\setup_neon_database.py"
```

O script cria as tabelas e índices sem inserir contas demonstrativas. Ele não substitui a revisão das migrações em bancos existentes.

O MongoDB deve estar disponível na conexão configurada. O banco e a coleção são utilizados pelo backend nas operações de catálogo.

### 4. Iniciar a API

Ainda em `api routes/`, com o ambiente virtual ativado:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs
- Especificação OpenAPI: http://localhost:8000/openapi.json

A conexão PostgreSQL é aberta por requisição e encerrada ao final, incluindo transações de leitura. O endpoint `/health` verifica a aplicação sem consultar os bancos. Em hospedagem, configure `DATABASE_URL` com SSL; no ambiente local, use as variáveis individuais e prefira `DB_PORT` para a porta do banco.

### 5. Iniciar o frontend

Em outro terminal, a partir da raiz:

```powershell
cd "front/nexus"
npm ci
npm run dev -- --port 5173 --strictPort
```

Acesse http://localhost:5173. Em desenvolvimento, o frontend usa `http://localhost:8000` por padrão, e o CORS permite `http://localhost:5173`. Utilize esses endereços de forma consistente ao testar os cookies. `VITE_API_URL` permite substituir a URL pública da API; em produção, sem essa variável, as chamadas usam a mesma origem da página.

## Endpoints

| Método | Rota | Finalidade | Autenticação |
| --- | --- | --- | --- |
| GET | `/health` | Verificar se a aplicação está respondendo, sem consultar bancos | Não |
| POST | `/register` | Cadastrar usuário | Não |
| POST | `/login` | Iniciar sessão | Não |
| POST | `/refresh` | Renovar tokens | Refresh token em cookie |
| POST | `/logout` | Revogar sessão e remover cookies | Cookie da sessão, quando presente |
| GET | `/users/me` | Consultar perfil e itens vinculados | Access token em cookie |
| PATCH | `/users/me` | Alterar nome | Access token em cookie |
| PATCH | `/users/me/password` | Alterar senha | Access token em cookie |
| DELETE | `/users/me/delete` | Excluir conta e dados relacionais vinculados | Access token em cookie |
| GET | `/library` | Listar biblioteca pessoal | Access token em cookie |
| POST | `/library` | Adicionar conteúdo usando provedor externo | Access token em cookie |
| POST | `/library/manual` | Cadastrar conteúdo manualmente | Access token em cookie |
| PATCH | `/library/{id}` | Atualizar status e/ou avaliação | Access token em cookie |
| PATCH | `/library/{id}/favorite` | Marcar ou desmarcar favorito | Access token em cookie |
| POST | `/get_mongo` | Buscar metadados dos conteúdos vinculados ao usuário | Access token em cookie |
| DELETE | `/library/{id}` | Remover item da biblioteca | Access token em cookie |

### Exemplos de requisição

Cadastro em `POST /register`:

```json
{
  "login": "pessoa_exemplo",
  "password": "SenhaLocal123!",
  "name": "Pessoa Exemplo"
}
```

Entrada em `POST /login`:

```json
{
  "login": "pessoa_exemplo",
  "password": "SenhaLocal123!"
}
```

Adição em `POST /library`, após o login:

```json
{
  "title": "Duna",
  "type": "movie"
}
```

Os tipos aceitos são `movie`, `game` e `book`.

Atualização em `PATCH /library/{id}`:

```json
{
  "status": "Assistido",
  "rating": 5
}
```

É possível enviar apenas `status` ou apenas `rating`. Os campos omitidos preservam seus valores atuais. Os status usados pela interface são `Quero Assistir`/`Assistido` para filmes, `Quero Jogar`/`Jogado` para jogos e `Quero Ler`/`Lendo`/`Lido` para livros.

Favoritar em `PATCH /library/{id}/favorite`:

```json
{
  "favorite": true
}
```

Envie `false` para remover dos favoritos. A escolha pertence ao usuário autenticado e não altera o status nem a avaliação.

Alterar o nome de exibição em `PATCH /users/me`:

```json
{
  "username": "Novo Nome"
}
```

Alterar a senha em `PATCH /users/me/password`:

```json
{
  "password": "NovaSenhaLocal123!"
}
```

A senha deve conter de 8 a 64 caracteres. A confirmação é validada pela interface; a API recebe apenas a nova senha. Para os demais modelos, consulte `/docs`.

## Testes

Na pasta `api routes/`, com o ambiente virtual ativado:

```powershell
# Executar os testes que não exigem PostgreSQL real
python -m pytest tests -v

# Executar toda a suíte, incluindo integração com PostgreSQL
python -m pytest tests -v --run-integration

# Executar somente os testes de integração
python -m pytest tests -v -m integration --run-integration
```

Os testes incluem cenários de cadastro, login, renovação e revogação de sessão, perfil, biblioteca, isolamento entre usuários, validação de entradas e falhas de serviços externos. Também há testes de favoritos, normalização do login, compatibilidade com contas antigas e migração de e-mail para login.

Os testes de integração leem `DBNAME`, `HOST`, `PORT`, `USER` e `PASSWORD` de `api routes/.env`, com fallback para as variáveis do processo. Eles não utilizam diretamente `DATABASE_URL` da aplicação. Se o PostgreSQL de testes usa porta diferente da padrão, defina `PORT` para essa execução.

Os testes de integração criam bancos temporários com prefixo `nexus_pytest_`, inicializam o esquema e removem os bancos ao finalizar. O usuário PostgreSQL configurado precisa ter permissão para criar bancos; interrupções abruptas podem impedir a limpeza.

MongoDB e os serviços externos são simulados na suíte. Portanto, esses testes não validam a disponibilidade nem as credenciais reais dos provedores. Detalhes adicionais estão em [tests/README.md](api%20routes/tests/README.md).

### Última validação

Em **16/11/2026**:

- Build React aprovado e imagem Docker compilada no Render.
- **187 testes aprovados**, incluindo integração com PostgreSQL.
- `npm audit` no frontend e na raiz: zero ocorrências reportadas após as correções.
- Consulta ao OSV para os 39 pacotes fixados em `requirements.txt`: nenhum aviso conhecido retornado.
- `pip check`: nenhuma dependência quebrada.
- Teste pelo endereço público: cadastro, login, perfil, biblioteca, cadastro manual, metadados no Atlas, favoritos, status, refresh e exclusão retornaram sucesso. Os registros de teste foram removidos.

O lint ainda aponta **quatro erros preexistentes** de `react-hooks/set-state-in-effect`, em `Books.jsx`, `Games.jsx`, `Movies.jsx` e `useLibrary.js`. A revisão de dependências cobre avisos conhecidos nas bases consultadas nessa data; não equivale a uma auditoria completa do código ou da imagem do sistema operacional. Veja o [relatório de dependências](docs/DEPENDENCIAS.md).

## Hospedagem

O Nexus está disponível em **[projeto-nexus-617m.onrender.com](https://projeto-nexus-617m.onrender.com)**.

| Componente | Ambiente atual |
| --- | --- |
| React e FastAPI | Um Web Service Docker no Render Free, na mesma origem HTTPS |
| PostgreSQL | Neon, branch production |
| MongoDB | MongoDB Atlas |
| Código | GitHub, branch auth |

O serviço atual foi criado pela opção **Public Git Repository**. Para publicar alterações:

1. Faça commit e Push da branch auth para o GitHub.
2. No painel do serviço no Render, selecione **Manual Deploy → Deploy latest commit**.
3. Acompanhe o build e confirme o estado **Live**. Verifique também os fluxos que dependem dos bancos; `/health` verifica apenas a aplicação.

O deploy automático ainda não está configurado. O `render.yaml` registra uma configuração reproduzível por Blueprint, mas não gerencia automaticamente o serviço criado manualmente. O `Dockerfile` compila o React e o serve pela API, incluindo acesso direto às rotas como `/perfil`.

Em produção, as credenciais ficam nas variáveis privadas do Render; os cookies são HttpOnly e Secure, com SameSite=Lax. O disco do serviço não é usado para persistir os dados dos usuários. Os dados do PostgreSQL local não foram importados para o Neon.

### Documentação complementar

| Documento | Conteúdo |
| --- | --- |
| [Guia de deploy](docs/DEPLOY.md) | Preparação de ambiente e publicação gratuita |
| [Integração Neon](docs/NEON.md) | Conexões, esquema, MCP e variáveis do PostgreSQL |
| [Revisão de dependências](docs/DEPENDENCIAS.md) | Atualizações de segurança, versões e validação |
| [Testes da API](api%20routes/tests/README.md) | Organização da suíte e integração |

## Próximas etapas

- [ ] Configurar backups dos dois bancos e validar restauração.
- [ ] Integrar renovação automática da sessão no frontend.
- [ ] Limitar tentativas de login.
- [ ] Corrigir os quatro erros de lint pendentes.
- [ ] Automatizar testes e verificações de dependências com GitHub Actions.
- [ ] Configurar deploy automático.
- [ ] Completar adicionados recentemente e filtrar “Acompanhando agora” por status.
- [ ] Adicionar edição de avaliações e reviews pela interface.
- [ ] Permitir escolher entre resultados de busca antes de adicionar.
- [ ] Avaliar cache conforme a necessidade de uso.

## Aprendizados aplicados

O Nexus foi criado para praticar o desenvolvimento de uma aplicação com regras de negócio e múltiplas dependências: modelagem relacional e documental, integração de APIs, autenticação, autorização por usuário, validação e testes de cenários de sucesso e falha.

## Autor

**Paulo Gabriel Lima Santos**

Desenvolvedor de Software Júnior com foco em backend Python.
