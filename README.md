# Nexus

**Biblioteca pessoal de filmes, jogos e livros, com foco em desenvolvimento backend Python.**

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

Para bancos existentes, pare a API e execute `api routes/migrations/004_users_login.sql` antes de reiniciar. A migração preserva o identificador antigo das contas como login (contas antigas continuam entrando com o endereço que usavam anteriormente). Não há envio ou verificação de e-mail.

### Biblioteca pessoal

- Adição, listagem e remoção de filmes, jogos e livros.
- Adição por título consultando o primeiro resultado do provedor externo.
- Cadastro manual de conteúdos em janelas flutuantes específicas para filmes, jogos e livros.
- Campos manuais para título, data, gêneros, URL da capa e direção/autores quando aplicável.
- Registro de status e avaliação.
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
React + JavaScript (em desenvolvimento)
                  |
             HTTP + cookies
                  |
             FastAPI / Python
                  |
       +----------+-----------+
       |                      |
   PostgreSQL              MongoDB
   - usuários              - catálogo de conteúdos
   - refresh tokens        - metadados dos provedores
   - biblioteca pessoal

O backend também consulta TMDB, IGDB e Open Library.
```

O PostgreSQL armazena os dados relacionais dos usuários e suas bibliotecas. O MongoDB armazena documentos de catálogo com campos que variam conforme o tipo de conteúdo e o provedor. A biblioteca referencia o identificador do documento de catálogo.

As rotas estão separadas em módulos de autenticação, usuários e biblioteca. A validação de entrada utiliza Pydantic, e o tratamento compartilhado de erros de banco está em `routers/db_errors.py`.

## Estado atual

| Área | Situação |
| --- | --- |
| API de autenticação, usuários e biblioteca | Implementada |
| Integrações com os três provedores | Implementadas |
| Persistência em PostgreSQL e MongoDB | Implementada |
| Testes automatizados e integração com PostgreSQL | Presentes no repositório |
| Frontend | Cadastro e entrada por login, sessão protegida, biblioteca, janelas de adição e perfil integrados |
| Dashboard | Biblioteca e favoritos integrados; seção de recentes ainda vazia e “Acompanhando agora” sem filtro por status |
| Docker e deploy | Dockerfile e Blueprint Render preparados; publicação ainda pendente |
| Redis e CI/CD | Planejados |

A implementação atual do frontend utiliza **JavaScript/JSX**. O projeto ainda exige ajustes para implantação em produção.

## Estrutura do projeto

```text
.
├── api routes/
│   ├── main.py
│   ├── requirements.txt
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
├── modelos/
└── README.md
```

## Executar localmente

### Pré-requisitos

- Python com suporte às dependências de `api routes/requirements.txt`.
- Node.js e npm compatíveis com a versão do Vite declarada em `front/nexus/package.json`.
- PostgreSQL e MongoDB acessíveis localmente ou por conexão remota.
- Credenciais TMDB e Twitch/IGDB para as respectivas integrações. A consulta atual à Open Library não utiliza chave de API.

Os comandos abaixo usam PowerShell e partem da raiz do repositório.

### 1. Preparar o backend

```powershell
cd "api routes"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Configurar as variáveis de ambiente

Crie `api routes/.env` com os nomes utilizados pelo código:

```dotenv
# PostgreSQL
DBNAME=nexus
HOST=localhost
PORT=5432
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

Mantenha o `.env` fora do versionamento. Os valores acima são exemplos e devem ser substituídos pela configuração do seu ambiente.

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
npm install
npm run dev -- --port 5173 --strictPort
```

Acesse http://localhost:5173. Atualmente, as chamadas do frontend apontam para `http://localhost:8000`, e o CORS do backend permite `http://localhost:5173`. Utilize esses endereços de forma consistente ao testar a sessão por cookies.

## Endpoints

| Método | Rota | Finalidade | Autenticação |
| --- | --- | --- | --- |
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
| POST | `/get_mongo` | Buscar metadados de catálogo a partir de IDs | Access token em cookie |
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

Os testes de integração criam bancos temporários com prefixo `nexus_pytest_`, inicializam o esquema e removem os bancos ao finalizar. O usuário PostgreSQL configurado precisa ter permissão para criar bancos; interrupções abruptas podem impedir a limpeza.

MongoDB e os serviços externos são simulados na suíte. Portanto, esses testes não validam a disponibilidade nem as credenciais reais dos provedores. Detalhes adicionais estão em [tests/README.md](api%20routes/tests/README.md).

## Hospedagem

O [guia de deploy gratuito](docs/DEPLOY.md) descreve a configuração com Render Free (React e FastAPI no mesmo endereço HTTPS), Neon Free (PostgreSQL) e MongoDB Atlas. O `render.yaml` e o `Dockerfile` estão na raiz. Nenhum serviço externo é criado automaticamente apenas por manter esses arquivos no repositório.

Em produção, o frontend usa a mesma origem da página; em desenvolvimento, mantém `http://localhost:8000`. A variável pública `VITE_API_URL` permite substituir esse endereço. Configure segredos somente no backend, conforme `api routes/.env.example`.

## Próximas etapas

- [ ] Permitir ao usuário armazenar seu próprio review sobre o conteúdo.

- [ ] Completar a seção de adicionados recentemente e filtrar “Acompanhando agora” por status.
- [ ] Adicionar edição de avaliações pela interface.
- [ ] Permitir escolher entre resultados de busca antes de adicionar.
- [ ] Integrar renovação automática da sessão no frontend.
- [ ] Ajustar e validar o comportamento de sessão para produção com HTTPS.
- [ ] Validar a imagem Docker no primeiro deploy e concluir a publicação.
- [ ] Avaliar Redis para cache.
- [ ] Automatizar verificações com GitHub Actions.
- [ ] Preparar e documentar o deploy.

## Aprendizados aplicados

O Nexus foi criado para praticar o desenvolvimento de uma aplicação com regras de negócio e múltiplas dependências: modelagem relacional e documental, integração de APIs, autenticação, autorização por usuário, validação e testes de cenários de sucesso e falha.

## Autor

**Paulo Gabriel Lima Santos**

Desenvolvedor de Software Júnior com foco em backend Python.

## Integração Neon

O PostgreSQL hospedado foi conectado e validado pela API. Consulte [configuração e validação do Neon](docs/NEON.md) para o esquema, MCP e variáveis de ambiente. A publicação da aplicação no Render continua pendente.
