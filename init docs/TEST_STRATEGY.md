# TEST_STRATEGY.md — Flight Hunter  
_Versão 0.1 • 10 Jul 2025_

> **Objetivo:** garantir qualidade, regressão zero e confiança para deploy
> contínuo desde o MVP até escala de milhares de usuários.

---

## 1 · Pirâmide de testes & metas de cobertura
| Camada                  | % alvo | Ferramentas         | SLAs de execução CI |
|-------------------------|--------|---------------------|---------------------|
| **Unit**               | ≈ 70 % | `pytest` + `pytest-mock` | < 60 s |
| **Integration**        | ≈ 25 % | `pytest` + `docker-compose` services (Postgres, Redis) | < 3 min |
| **End-to-End (E2E)**   | ≈ 5 %  | `Playwright` (API + Telegram bot) | < 4 min |
| **Load/Perf** (opcional)| n/a   | `Locust` (no CI, stage) | — |

### Cobertura de linhas **mín. 80 %** no backend (`pytest-cov`) — mas foco em caminhos críticos, não em números absolutos.

---

## 2 · Matriz de casos críticos
| Módulo | Cenário | Tipo de teste |
|--------|---------|---------------|
| **Watchlist API** | Criar rota válida → `201` | Unit (validator) + Integration |
| | Criar rota duplicada → `409` | Unit |
| | Token ausente → `401` | Unit |
| **Price Fetcher** | Índice de 4 ↓ preço‐alvo → grava `price_cache` | Integration (mock Amadeus) |
| | Nenhuma oferta → não grava | Unit |
| **Alert Engine** | Queda de preço → envia e-mail &/ou Telegram uma vez (não duplica) | Integration |
| | Preço acima‐alvo → **não** alerta | Unit |
| **Stripe Webhook** | `checkout.session.completed` cria/atualiza plano → user `plan=PRO` | Integration (mock Stripe CLI) |
| | Assinatura cancelada → retrograde para `FREE` | Integration |
| **Duffel Link** | Gerar link com parâmetros corretos | Unit |
| **Auth/JWT** | Token expira → `401` | Unit |
| **Agent Pacote Duplo** | Entrada mock → JSON que respeita schema & regras (≤1 escala etc.) | Unit (schema) |
| **Telegram Bot** | Comando `/settings` devolve lista de rotas | E2E (Playwright→Bot API) |

---

## 3 · Ferramentas & bibliotecas
| Propósito | Lib |
|-----------|-----|
| Mock HTTP externos | `responses` (unit) · `pytest-vcr` (integration) |
| Database fixtures  | `pytest-postgres`, `pytest-asyncio` |
| Docker services    | `docker-compose -f tests/docker-compose.yml up -d` |
| Schema validation  | `pydantic` + OpenAPI-generated clients |
| Coverage & lint    | `pytest-cov`, `ruff` |
| Load tests         | `locustfile.py` (staging only) |

---

## 4 · Pipeline CI (GitHub Actions excerpt)
```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: [5432:5432]
      redis:
        image: redis:7-alpine
        ports: [6379:6379]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install -r requirements-dev.txt
      - run: pytest -q --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3
```
(E2E Playwright roda em job separado, tipo jobs.e2e com npx playwright test.)

## 5 · Princípios de design de testes
1. Determinismo – nada de chamadas a API reais nas suites de CI.
2. Isolamento – cada teste cria/limpa seus dados (fixtures + rollback).
3. Fail-fast – assertivas curtas; logs caplog habilitado em CI.
4. Contrato – integração valida payload vs. API_SPEC.md com schemathesis.
5. Observabilidade – falhas E2E enviam screenshot/video ao artefato de CI.

## 6 · Performance & Resiliência
* Rodar Locust em staging toda sexta:
    * 200 rps por 60 s endpoint /watchlist
    * 20 rps job fetch_prices
* Meta: p95 latência API < 250 ms; error-rate < 1 %.
*Stress test trimestral com chaostoolkit (simular falha Redis, lentidão Amadeus).

7 · Critérios de Definition of Done
 Cobertura automática do caso na matriz crítica.
 Todos testes verdes em CI principal.
 Lint e format sem avisos (ruff, black).
 Atualização do CHANGELOG quando alterar comportamento público.

Revisão deste documento a cada release ou mudança de suíte de testes.