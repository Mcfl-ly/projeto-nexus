# Revisão de dependências — 16/11/2026

## Resultado

- Frontend: npm audit passou de 4 ocorrências (3 moderadas, 1 alta) para zero.
- Dependências Node da raiz (ferramentas Neon): npm audit retornou zero.
- Backend: consulta ao OSV identificou avisos em 4 dos 42 pacotes fixados; após a correção, os 39 pacotes mantidos não retornaram avisos conhecidos. Todas as respostas foram verificadas sem paginação pendente.

## Alterações

| Pacote | Antes | Depois |
| --- | --- | --- |
| eslint | 10.12.0 | 10.15.0 |
| @eslint/config-array | 0.23.5 | 0.23.6 |
| minimatch | 10.2.6 | 11.0.8 |
| zod | 4.6.5 | 4.6.7 |
| brace-expansion | 5.0.12 | 5.0.13 |
| @isaacs/nonrecursive-glob-match | não instalado | 1.1.0 (dependência transitiva) |
| dnspython | 2.9.0 | 2.9.2 |
| opentelemetry-api | 1.45.1 | 1.45.2 |
| deep-translator, beautifulsoup4, soupsieve | presentes | removidos |

A cadeia de tradução/HTML removida não era utilizada: havia apenas um import sem uso de GoogleTranslator em routers/library/routes.py. O fallback opcional existente usa Argos; ele foi preservado. OpenTelemetry continua instalado porque é uma dependência do FastAPI.

As atualizações Node foram resolvidas por npm audit fix sem --force, mantendo as faixas do package.json. As ocorrências Node estavam nas ferramentas de desenvolvimento; não se constatou por essa auditoria que os fluxos públicos da aplicação estivessem exploráveis.

## Validação

- npm run build: aprovado.
- npm audit no frontend, incluindo dependências de desenvolvimento: zero vulnerabilidades.
- npm audit --omit=dev: zero vulnerabilidades.
- npm audit na raiz: zero vulnerabilidades.
- pip check: nenhuma dependência quebrada.
- pytest tests -q --run-integration: 187 passed in 13.93s.
- npm run lint: quatro erros preexistentes react-hooks/set-state-in-effect em Books.jsx, Games.jsx, Movies.jsx e useLibrary.js. Não foram desabilitados nem ocultados.

A consulta Python foi feita diretamente pela API do OSV para cada nome e versão de requirements.txt. A tentativa de instalar pip-audit em ambiente isolado de ferramentas foi interrompida devido à lentidão; ele não foi adicionado às dependências da aplicação.

## Escopo

Este resultado cobre avisos conhecidos nas bases consultadas nessa data, não uma garantia de ausência de falhas. Não inclui auditoria dos pacotes Debian da imagem Docker nem análise completa do código. As correções só entram no site hospedado após Push e um novo deploy no Render.

## Fontes

- https://github.com/advisories/GHSA-g3hv-75wg-m249
- https://github.com/advisories/GHSA-mrhx-c7xc-m3w5
- https://github.com/rthalley/dnspython/security/advisories/GHSA-vvf4-9x63-8xvv
- https://github.com/open-telemetry/opentelemetry-python/security/advisories/GHSA-mf5v-w3w3-f6cg
- https://github.com/pypa/advisory-database/blob/main/vulns/deep-translator/PYSEC-2022-252.yaml
- https://github.com/facelessuser/soupsieve/security/advisories/GHSA-mmhr-3c5m-f64f
- https://google.github.io/osv.dev/post-v1-querybatch/
