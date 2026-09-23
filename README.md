# 📚 Nexus

> Plataforma Full Stack para gerenciamento de uma biblioteca pessoal de filmes, jogos e livros.

O **Nexus** é uma aplicação desenvolvida para permitir que usuários pesquisem, adicionem e acompanhem conteúdos que desejam consumir.

O projeto combina **FastAPI, React, PostgreSQL e MongoDB**, além de integrar diferentes APIs externas para obtenção de informações sobre filmes, jogos e livros.

O principal objetivo do projeto é aplicar conceitos de desenvolvimento de software em um cenário próximo de uma aplicação real, incluindo **autenticação, autorização, segurança, persistência de dados, integração com APIs externas e regras de negócio**.

---

## ✨ Funcionalidades

### 👤 Autenticação

* Cadastro de usuários
* Login e logout
* Access Token utilizando JWT
* Refresh Token utilizando JWT
* Rotação de Refresh Tokens
* Revogação de tokens
* Cookies `HttpOnly`
* Hash de senhas utilizando Argon2
* Rotas protegidas

### 📚 Biblioteca pessoal

Cada usuário possui sua própria biblioteca.

É possível:

* Adicionar conteúdos
* Listar conteúdos
* Alterar status
* Atribuir avaliação
* Atualizar parcialmente um conteúdo
* Remover conteúdos
* Adicionar conteúdos manualmente

### 🔎 Busca de conteúdos

O sistema utiliza diferentes fontes dependendo do tipo de conteúdo:

| Tipo      | Fonte        |
| --------- | ------------ |
| 🎬 Filmes | TMDB         |
| 🎮 Jogos  | IGDB         |
| 📚 Livros | Open Library |

O catálogo é armazenado no **MongoDB**, enquanto a relação entre usuário e conteúdo é armazenada no **PostgreSQL**.

---

# 🏗️ Arquitetura

A aplicação utiliza uma arquitetura híbrida, separando os dados de catálogo dos dados relacionados aos usuários.

```text
                         ┌─────────────────────┐
                         │      FRONTEND       │
                         │   React + TypeScript│
                         └──────────┬──────────┘
                                    │
                               HTTP / REST
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FASTAPI       │
                         │       Backend       │
                         └─────────┬───────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   │                               │
                   ▼                               ▼
        ┌─────────────────────┐         ┌─────────────────────┐
        │     PostgreSQL      │         │       MongoDB       │
        │                     │         │                     │
        │ • Usuários          │         │ • Filmes            │
        │ • Refresh Tokens    │         │ • Jogos             │
        │ • Biblioteca        │         │ • Livros            │
        │ • Status            │         │ • Dados externos    │
        │ • Avaliações        │         │                     │
        └─────────────────────┘         └──────────┬──────────┘
                                                   │
                                      ┌────────────┼────────────┐
                                      │            │            │
                                      ▼            ▼            ▼
                                    TMDB         IGDB      Open Library
```

### Por que dois bancos?

**PostgreSQL** é utilizado para dados relacionais e transacionais, como usuários, autenticação e bibliotecas pessoais.

**MongoDB** é utilizado como catálogo de conteúdos, permitindo armazenar documentos provenientes de diferentes APIs externas com estruturas que podem variar entre si.

Essa separação evita misturar o catálogo global com os dados privados de cada usuário.

---

# 🛠️ Stack

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)

* Python
* FastAPI
* Pydantic
* Psycopg
* PyJWT
* Argon2

### Frontend

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge\&logo=react\&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge\&logo=typescript\&logoColor=white)

* React
* TypeScript

### Banco de dados

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge\&logo=postgresql\&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge\&logo=mongodb\&logoColor=white)

* PostgreSQL
* MongoDB

### APIs externas

* 🎬 TMDB
* 🎮 IGDB
* 📚 Open Library

---

# 🔐 Autenticação e segurança

A autenticação utiliza **JWT com Access Token e Refresh Token**.

```text
                    LOGIN
                      │
                      ▼
              Validação da senha
                      │
                      ▼
             ┌─────────────────┐
             │   Argon2 Hash   │
             └────────┬────────┘
                      │
                      ▼
             Geração dos tokens
                      │
             ┌────────┴────────┐
             ▼                 ▼
        Access Token      Refresh Token
          curto              longo
             │                 │
             │                 ▼
             │          PostgreSQL
             │
             ▼
       Rotas protegidas
```

### Access Token

Utilizado para autorizar as requisições autenticadas.

Possui duração curta para reduzir o impacto de uma eventual exposição.

### Refresh Token

Permite gerar novos Access Tokens sem exigir que o usuário faça login novamente.

Os Refresh Tokens são armazenados no banco de dados e podem ser **revogados e rotacionados**.

### Proteções utilizadas

* 🔒 Argon2 para senhas
* 🔑 JWT
* 🍪 Cookies `HttpOnly`
* 🛡️ Rotas protegidas
* 🔄 Rotação de Refresh Tokens
* 🚫 Revogação de sessões
* 👤 Isolamento da biblioteca por usuário

---

# 📖 Biblioteca do usuário

A biblioteca utiliza uma relação entre o usuário e o conteúdo.

```text
             USER
              │
              │ 1:N
              ▼
        USER_LIBRARY
              │
              │ N:1
              ▼
           CONTENT
```

Um registro da biblioteca contém informações como:

```text
user_id
content_id
name
status
rating
created_at
external_api_id
```

Isso permite que diferentes usuários adicionem o mesmo conteúdo às suas bibliotecas sem duplicar o conteúdo no catálogo.

---

# 🔎 Fluxo de busca

A aplicação evita consultar APIs externas sempre que o conteúdo já estiver disponível no catálogo.

```text
                    Pesquisa
                       │
                       ▼
                 ┌───────────┐
                 │  MongoDB  │
                 └─────┬─────┘
                       │
                ┌──────┴──────┐
                │             │
             Encontrou     Não encontrou
                │             │
                │             ▼
                │       API externa
                │             │
                │       ┌─────┴─────┐
                │       │           │
                │    Encontrou   Não encontrou
                │       │           │
                │       ▼           ▼
                │    MongoDB    Cadastro manual
                │       │           │
                └───────┴───────────┘
                            │
                            ▼
                    Biblioteca do usuário
```

Esse fluxo reduz chamadas desnecessárias às APIs externas e permite manter um catálogo local.

---

# 🎬 Filmes

Os filmes são obtidos através da **TMDB API**.

Informações utilizadas:

* Título
* Título original
* Sinopse
* Data de lançamento
* Gêneros
* Identificador externo
* Imagem de capa

---

# 🎮 Jogos

Os jogos são obtidos através da **IGDB API**.

Informações utilizadas:

* Nome
* Sinopse
* Data de lançamento
* Gêneros
* Capa
* Identificador externo

Também foi considerada a utilização de `game_localizations` para priorizar informações localizadas em português.

---

# 📚 Livros

Os livros são obtidos através da **Open Library API**.

Informações utilizadas:

* Título
* Autor
* Identificador da obra
* Data de publicação
* Assuntos/gêneros
* Capa

Os assuntos retornados pela API são tratados antes de serem armazenados para gerar uma lista de gêneros mais adequada.

---

# 🌎 Normalização de dados

Como diferentes APIs podem utilizar títulos diferentes para o mesmo conteúdo, o backend possui uma etapa de normalização.

O processo inclui:

* Conversão para lowercase
* Remoção de acentos
* Normalização de texto
* Tratamento de títulos equivalentes

Exemplo:

```text
De Volta para o Futuro 3
```

pode ser normalizado para facilitar a comparação com outras fontes.

Essa estratégia ajuda a reduzir duplicidades e melhorar as buscas.

---

# 📝 Cadastro manual

Caso um conteúdo não seja encontrado nas fontes externas, o usuário pode cadastrá-lo manualmente.

Isso permite que o sistema continue funcionando mesmo quando determinado conteúdo não estiver disponível nas APIs utilizadas.

```text
API externa
     │
     ├── Encontrado ──► Catálogo
     │
     └── Não encontrado
              │
              ▼
       Cadastro manual
              │
              ▼
           Catálogo
```

---

# 🌐 API REST

A API é construída utilizando **FastAPI**.

Principais grupos de endpoints:

```text
/auth
/users
/library
/content
```

### Authentication

```http
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

### Users

```http
GET   /users/me
PATCH /users/me
```

### Library

```http
GET    /library
POST   /library
PATCH  /library/{id}
DELETE /library/{id}

POST   /library/manual
```

---

# 🔄 PATCH e atualização parcial

A atualização da biblioteca utiliza `PATCH`, permitindo alterar somente os campos desejados.

Por exemplo:

```json
{
  "status": "Concluído"
}
```

Somente o status será alterado.

Também é possível enviar:

```json
{
  "rating": 5
}
```

Nesse caso, o status atual permanece intacto.

Isso evita que informações existentes sejam sobrescritas desnecessariamente.

---

# 🗄️ Modelo de dados

### PostgreSQL

Responsável principalmente pelos dados relacionados aos usuários:

```text
users
   │
   ├── refresh_tokens
   │
   └── user_library
             │
             ▼
         content_id
```

### MongoDB

Responsável pelo catálogo:

```text
contents
   │
   ├── movies
   ├── games
   ├── books
   └── manual
```

A estrutura do documento pode conter:

```json
{
  "external_api": "tmdb",
  "external_api_id": "123456",
  "title": "Título",
  "description": "Descrição",
  "release_date": "2025-01-01",
  "genres": [],
  "cover": "..."
}
```

# ⚙️ Configuração

## 1. Clone o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_PROJETO>
```

## 2. Crie o ambiente virtual

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 4. Configure o `.env`

Crie um arquivo `.env` baseado no `.env.example`.

```env
DATABASE_URL=

MONGODB_CONNECTION_STRING=
DATABASE=
COLECAO=

SECRET_KEY=
ALGORITHM=

TMDB_KEY=

IGDB_CLIENT_ID=
IGDB_CLIENT_SECRET=
```

> ⚠️ Nunca versione o arquivo `.env` contendo credenciais reais.

## 5. Execute o backend

```bash
uvicorn main:app --reload
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 Testes

A estratégia de testes do projeto será baseada em **Pytest**.

Áreas previstas:

```text
Authentication
    ├── Register
    ├── Login
    ├── Refresh
    └── Logout

Library
    ├── Create
    ├── Read
    ├── Update
    └── Delete

Content
    ├── Search
    ├── External APIs
    └── Manual creation
```

---

# 📊 Status do projeto

### Backend

* [x] Cadastro de usuários
* [x] Login
* [x] Logout
* [x] JWT Access Token
* [x] JWT Refresh Token
* [x] Rotação de Refresh Token
* [x] Revogação de tokens
* [x] Argon2
* [x] Cookies HttpOnly
* [x] Rotas protegidas
* [x] Biblioteca por usuário
* [x] Adição de conteúdo
* [x] Atualização parcial
* [x] Remoção de conteúdo
* [x] Status
* [x] Avaliação
* [x] Cadastro manual

### Integrações

* [x] TMDB
* [x] IGDB
* [x] Open Library
* [x] MongoDB como catálogo
* [x] Normalização de títulos

### Frontend

* [ ] Interface React
* [ ] Autenticação
* [ ] Dashboard
* [ ] Biblioteca
* [ ] Busca
* [ ] Página de detalhes

### Infraestrutura

* [ ] Docker
* [ ] Redis
* [ ] Pytest
* [ ] GitHub Actions
* [ ] Deploy

---

# 🚧 Roadmap

```text
[x] Backend API
[x] Authentication
[x] PostgreSQL
[x] MongoDB
[x] External APIs
[x] Personal library

[ ] React frontend
[ ] Automated tests
[ ] Docker
[ ] Redis
[ ] CI/CD
[ ] Production deployment
```

### Próximas etapas

* Desenvolver a interface React + TypeScript
* Implementar testes automatizados
* Dockerizar os serviços
* Adicionar Redis para cache
* Configurar CI com GitHub Actions
* Preparar ambiente de produção
* Melhorar sistema de busca
* Criar dashboard com estatísticas
* Adicionar reviews e anotações

---

# 🎯 Objetivos técnicos

Este projeto foi desenvolvido como um projeto de portfólio com foco em **Backend Python e desenvolvimento Full Stack**.

Os principais conceitos praticados incluem:

* Desenvolvimento de APIs REST
* FastAPI
* Autenticação JWT
* Access e Refresh Tokens
* Cookies HttpOnly
* Hash de senhas com Argon2
* PostgreSQL
* MongoDB
* Modelagem de dados
* Integração com APIs externas
* Normalização de dados
* Regras de negócio
* Controle de acesso
* Atualização parcial com PATCH
* Separação entre catálogo e dados privados
* Tratamento de fallback
* Arquitetura de aplicações Full Stack

---

# 👨‍💻 Autor

**Paulo Gabriel**

Desenvolvedor de Software Júnior com foco em **Backend Python e desenvolvimento Full Stack**.

Tecnologias principais:

`Python` · `FastAPI` · `PostgreSQL` · `MongoDB` · `React` · `TypeScript`

---

⭐ Se este projeto foi útil ou interessante, considere deixar uma estrela no repositório.
