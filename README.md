# Nexus

**Biblioteca pessoal de filmes, jogos e livros, com foco em desenvolvimento backend Python.**

O Nexus é um projeto pessoal de portfólio para organizar conteúdos em um só lugar. A API permite manter uma biblioteca individual, acompanhar o status de cada item e registrar avaliações, integrando informações de três serviços externos.

O projeto reúne autenticação com JWT, controle de acesso por usuário, persistência em PostgreSQL e MongoDB e testes automatizados. A interface web em React está em desenvolvimento.

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

- Cadastro e login com validação de dados.
- Hash de senhas com Argon2.
- Access token JWT com duração de 15 minutos.
- Refresh token JWT com duração de 30 dias, armazenado como hash no PostgreSQL.
- Rotação de refresh tokens e revogação no logout.
- Armazenamento dos tokens no navegador por cookies HttpOnly.
- Consulta de perfil, alteração de nome e senha e exclusão da conta.

### Biblioteca pessoal

- Adição, listagem e remoção de filmes, jogos e livros.
- Cadastro manual de conteúdos.
- Registro de status e avaliação.
- Atualização parcial com PATCH, preservando os campos não enviados.
- Consultas e alterações da biblioteca vinculadas ao usuário autenticado.

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
| Frontend | Em desenvolvimento: cadastro, login, verificação de sessão e estrutura das páginas |
| Dashboard e apresentação dos conteúdos | Integração parcial; ainda há dados de exemplo na interface |
| Docker, Redis, CI/CD e deploy | Planejados |

A implementação atual do frontend utiliza **JavaScript/JSX**. O projeto ainda exige ajustes para implantação em produção.

## Estrutura do projeto

```text
.
├── api routes/
│   ├── main.py
│   ├── requirements.txt
│   ├── routers/
│   │   ├── auth/routes.py
│   │   ├── library/routes.py
│   │   ├── users/routes.py
│   │   └── db_errors.py
│   └── tests/
├── front/nexus/
│   ├── package.json
│   └── src/
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

Crie o banco informado em `DBNAME`. No arquivo `originais/sql_proj.psql`, execute **somente os três comandos CREATE TABLE iniciais**, que definem `users`, `refreshToken` e `userLibrary`.

O restante do arquivo contém INSERTs demonstrativos com senhas e tokens fictícios; esses registros não constituem contas válidas para autenticação.

Para bancos antigos sem `external_api_id` e `content_type`, consulte `originais/migrations/001_library_columns.sql` antes de executar a API.

O MongoDB deve estar disponível na conexão configurada. O banco e a coleção são utilizados pelo backend nas operações de catálogo.

### 4. Iniciar a API

Ainda em `api routes/`, com o ambiente virtual ativado:

```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs
- Especificação OpenAPI: http://localhost:8000/openapi.json

O PostgreSQL precisa estar disponível ao iniciar a aplicação, pois os módulos de rotas abrem conexões durante a importação.

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
| DELETE | `/library/{id}` | Remover item da biblioteca | Access token em cookie |

### Exemplos de requisição

Cadastro em `POST /register`:

```json
{
  "email": "pessoa@example.com",
  "password": "SenhaLocal123!",
  "name": "Pessoa Exemplo"
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
  "status": "Concluído",
  "rating": 5
}
```

É possível enviar apenas `status` ou apenas `rating`. Os campos omitidos preservam seus valores atuais. Para os demais modelos, consulte `/docs`.

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

Os testes incluem cenários de cadastro, login, renovação e revogação de sessão, perfil, biblioteca, isolamento entre usuários, validação de entradas e falhas de serviços externos.

Os testes de integração criam bancos temporários com prefixo `nexus_pytest_`, inicializam o esquema e removem os bancos ao finalizar. O usuário PostgreSQL configurado precisa ter permissão para criar bancos; interrupções abruptas podem impedir a limpeza.

MongoDB e os serviços externos são simulados na suíte. Portanto, esses testes não validam a disponibilidade nem as credenciais reais dos provedores. Detalhes adicionais estão em [tests/README.md](api%20routes/tests/README.md).

## Próximas etapas

- [ ] Concluir a integração das páginas React com a biblioteca e os metadados do catálogo.
- [ ] Substituir os dados de exemplo do dashboard por dados reais.
- [ ] Completar os fluxos da interface para busca, cadastro manual, edição e remoção.
- [ ] Ajustar e validar o comportamento de sessão para produção com HTTPS.
- [ ] Containerizar os serviços com Docker.
- [ ] Avaliar Redis para cache.
- [ ] Automatizar verificações com GitHub Actions.
- [ ] Preparar e documentar o deploy.

## Aprendizados aplicados

O Nexus foi criado para praticar o desenvolvimento de uma aplicação com regras de negócio e múltiplas dependências: modelagem relacional e documental, integração de APIs, autenticação, autorização por usuário, validação e testes de cenários de sucesso e falha.

## Autor

**Paulo Gabriel Lima Santos**

Desenvolvedor de Software Júnior com foco em backend Python.
