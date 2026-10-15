# Testes da API Nexus

Execute a partir de `E:\projeto novo\api routes`, com o mesmo Python da API:

```powershell
python -m pytest tests -v
python -m pytest tests -v --run-integration
python -m pytest tests -v -m integration --run-integration
```

O primeiro comando pula a integracao. O segundo executa tudo. O terceiro
executa somente os testes marcados como integracao.

Dependencias adicionais: pytest e httpx, alem das dependencias da API.
O aviso de descontinuacao httpx/Starlette atualmente nao impede a execucao.

## Isolamento

- PostgreSQL real somente com `--run-integration`. As credenciais sao lidas
  do `.env` da API, localmente. O usuario precisa poder criar bancos.
- Cada teste de integracao cria um banco `nexus_pytest_<uuid>`, inicializa as
  tres tabelas de `originais/sql_proj.psql` e remove o banco no teardown,
  inclusive quando uma assercao falha. Interromper o processo abruptamente
  pode impedir o teardown.
- Os INSERTs de exemplo do script nao sao executados. Nenhum registro do
  banco principal e alterado.
- MongoDB, traducao Argos e APIs externas sao simulados. HTTP externo via
  requests e bloqueado por padrao; os testes de servicos fornecem respostas
  e erros controlados. Integracao real com esses servicos nao esta coberta.
- Os testes usam chave JWT exclusiva de teste e HTTPS no TestClient para
  exercitar os cookies Secure. Nao e necessario iniciar Uvicorn.
- As rotas reais sao montadas numa aplicacao FastAPI de teste. Isso evita
  conexoes e downloads executados pelo projeto durante a importacao.

## Organizacao

- test_auth.py: validacao inicial do cadastro.
- test_register.py / test_register_integration.py: cadastro valido.
- test_auth_flows.py: cadastro, login, cookies, logout, refresh e erros.
- test_users_flows.py: autenticacao, perfil, nome, senha e exclusao.
- test_library_flows.py: biblioteca, validacao, permissoes e APIs simuladas.
- test_api_integration.py: fluxos completos, persistencia e isolamento entre
  usuarios no PostgreSQL temporario.
- conftest.py: fixtures, simulacoes e ciclo de vida dos bancos temporarios.

## Contratos esperados e falhas

Os testes documentam os contratos corrigidos: conflito de cadastro
retorna 409; entrada invalida retorna 422; recurso ausente retorna 404 (ou
401 quando a identidade deixou de existir); falha de um servico externo
retorna 502/503/504; falhas de escrita exigem rollback. Os testes nao
consideram 500 inesperado nem sucesso com dados invalidos como aprovacao.

O contrato atual de cadastro valido (200 com JSON null) foi preservado.
O DELETE de item ausente pode ser idempotente: o teste de isolamento aceita
200/204/404, mas exige que o registro de outro usuario continue intacto.

O schema de integracao vem do script do repositorio. Erros por colunas
ausentes mostram uma divergencia entre esse script e as rotas; nao provam
que essas colunas estejam ausentes no banco principal em uso.

Ultima execucao completa: 139 casos aprovados, nenhuma falha e um aviso,
em 15/10/2026. Os 25 casos que antes falhavam agora passam. Foram adicionados
26 casos em test_fixes_regression.py para erros de banco, renovacao atomica,
respostas externas, fechamento de cliente Mongo e migracao SQL idempotente.

A migracao originais/migrations/001_library_columns.sql atende bancos antigos
sem external_api_id e content_type. No banco configurado no Nexus, ambas as
colunas ja existiam, portanto a migracao nao foi aplicada ali.
