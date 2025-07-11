# Flight Hunter — MVP

> **Alfa privado** · Julho 2025  
> Rastreador de tarifas aéreas + alerta em tempo real + link de compra em 1 clique.

---

## Sumário
1. [Visão geral](#visão-geral)
2. [Funcionalidades](#funcionalidades)
3. [Arquitetura](#arquitetura)
4. [Stack & dependências](#stack--dependências)
5. [Configuração rápida](#configuração-rápida)
6. [Scripts disponíveis](#scripts-disponíveis)
7. [Estrutura do projeto](#estrutura-do-projeto)
8. [Roadmap curto](#roadmap-curto)
9. [Contribuindo](#contribuindo)
10. [Licença](#licença)

---

## Visão geral
Flight Hunter monitora preços de passagens para rotas escolhidas pelo usuário.  
Quando o valor cai abaixo do **preço-alvo**, o bot envia um alerta (e-mail ou Telegram) com um **Duffel Link** que permite comprar a passagem instantaneamente, já com o nosso markup embutido.

Objetivo do MVP: **100 clientes pagantes** usando um plano de assinatura simples (Free x Pro).

---

## Funcionalidades
| Status | Módulo | Descrição |
|--------|--------|-----------|
| ✅ | Cadastro de *watchlist* | Origem, destino, datas, flexibilidade, preço-alvo |
| ✅ | Crawler Amadeus | 4 varreduras/dia · cache em Postgres |
| ✅ | Alertas | E-mail (SendGrid) • Telegram Bot |
| ✅ | Duffel Links | Cria link de compra em 1 clique |
| 🔄 | Stripe Billing | Plano Free (2 alertas) / Pro (ilimitado) |
| 🕒 | Painel Metrics | Metabase Cloud para logs e KPIs |

---

## Arquitetura
```mermaid
graph TD
    A[Cloud Scheduler] -->|cron| B(Backend FastAPI)
    B --> C{Amadeus API}
    B --> D(PostgreSQL)
    B -->|price drop| E[SendGrid]
    B -->|price drop| F[Telegram Bot]
    B --> G{Duffel Links}
    H(Stripe Webhooks) --> B

Stack & dependências
| Camada          | Tech                              |
| --------------- | --------------------------------- |
| Linguagem       | Python 3.12                       |
| Web API         | **FastAPI** + Uvicorn             |
| Banco           | **PostgreSQL 16** (RDS free-tier) |
| Cache           | Redis (opcional)                  |
| Flights         | **Amadeus Self-Service API**      |
| Booking         | **Duffel Links**                  |
| Notificações    | SendGrid · Telegram Bot API       |
| Pagamentos      | Stripe Checkout + Billing         |
| Observabilidade | Sentry + Metabase Cloud           |

Configuração rápida
1. Clone e crie o ambiente
git clone https://github.com/seuusuario/flight-hunter.git #ainda precisa ser criado
cd flight-hunter
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

2. Variáveis de ambiente
Crie .env (ou copie .env.example):
DATABASE_URL=postgresql://user:pass@localhost/flight_hunter
AMADEUS_CLIENT_ID=xxx
AMADEUS_CLIENT_SECRET=xxx
DUFFEL_TOKEN=xxx
SENDGRID_API_KEY=xxx
STRIPE_SECRET_KEY=xxx
TELEGRAM_BOT_TOKEN=xxx

3. Migrações & seed
alembic upgrade head
python app/seed.py        # cria usuários de teste

4. Subir localmente
uvicorn app.main:app --reload

Swagger UI disponível em http://localhost:8000/docs.

Scripts disponíveis
| Comando          | O que faz                                 |
| ---------------- | ----------------------------------------- |
| `make dev`       | Roda app com reload + worker de scheduler |
| `make test`      | Executa testes Pytest                     |
| `make lint`      | Format & lint (ruff / black)              |
| `make docker-up` | Sobe stack local com Docker Compose       |

Estrutura do projeto
app/
 ├── api/            # rotas FastAPI
 ├── core/           # configs & utilidades
 ├── models/         # SQLModel ORM
 ├── services/       # Amadeus, Duffel, Stripe, etc.
 ├── workers/        # jobs de scheduler
 └── templates/      # e-mails, msgs Telegram

Roadmap curto
 Stripe → plano Pro totalmente funcional
 Job de limpeza de cache (TTL)
 Painel Metabase com métricas: MAU, Retenção 30 d, Alertas enviados
 Testes de carga (Locust) antes do beta aberto

Contribuindo
Este repositório começa privado; pull requests apenas do core team.
Abra issues para bugs ou ideias.

Licença
MIT © 2025-presente, Felipe L. da Fonseca
Revisar antes do open-source público.