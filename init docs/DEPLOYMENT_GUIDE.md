# DEPLOYMENT_GUIDE.md — Flight Hunter  
_Versão 0.1 • 10 Jul 2025_

> **Objetivo:** padronizar a forma de subir o backend e serviços auxiliares  
> em **ambiente local**, **staging** (Render.com) e **produção** (AWS).

---

## 1 · Diagramas de alto nível

### 1.1 Docker Compose (local dev)

┌──────────┐ 8000/tcp ┌──────────┐
│ backend  │◀────────▶│ postgres │
│ fastapi  │          └──────────┘
│          │          ┌───────┐
│          │◀──6379──▶│ redis │
└──────────┘          └───────┘
▲ ▲ ▲
│ │ 443 │
│ │ │
│ └───────→ SendGrid (API) │
└─────────→ Amadeus, Duffel, Stripe (HTTPS)


### 1.2 Render (staging)
```shell
Web Service (FastAPI)
└─ linked Postgres (Render PostgreSQL)
└─ linked Redis (optional) (Upstash Redis)
└─ Background Cron (Render Cron Job: price_fetch)
```

### 1.3 Produção (AWS; blueprint)
```shell
ALB (HTTPS) ──▶ ECS Fargate Service (backend)
            │
┌───────────┴────────────┐
│                        │
RDS Postgres ElastiCache Redis
```
---

## 2 · Pré-requisitos

| Ferramenta | Versão mínima | Obs. |
|------------|---------------|------|
| Docker / Docker Compose | 24.x | Inclui BuildKit |
| AWS CLI | 2.x | se usar deploy prod |
| Render CLI | n/a | Deploy via painel web |
| Terraform | 1.7+ | (opcional) IaC prod |
| Python | 3.12 | local scripts |

---

## 3 · Variáveis de ambiente (.env)

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DATABASE_URL` | Conexão Postgres | `postgresql://user:pass@db/flight_db` |
| `REDIS_URL` | Cache Redis | `redis://cache:6379/0` |
| `AMADEUS_CLIENT_ID` / `AMADEUS_CLIENT_SECRET` | Credenciais API | — |
| `DUFFEL_TOKEN` | API key booking | — |
| `SENDGRID_API_KEY` | E-mail | — |
| `STRIPE_SECRET_KEY` | Pagamentos | — |
| `STRIPE_WEBHOOK_SECRET` | Verificação assinatura | — |
| `TELEGRAM_BOT_TOKEN` | Bot | — |
| `APP_ENV` | `local` · `staging` · `prod` | |

Copie `.env.example` → `.env` e preencha.

---

## 4 · Deploy local (Docker Compose)

```bash
# 1. Subir stack
docker compose up -d --build

# 2. Rodar migrações
docker compose exec backend alembic upgrade head

# 3. Acessar
open http://localhost:8000/docs
```

## docker-compose.yml inclui:
```yaml
services:
  backend:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    env_file: .env
    depends_on: [db, redis]
    ports: ["8000:8000"]

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: flight_db
      POSTGRES_USER: flight
      POSTGRES_PASSWORD: flight_pw
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes: [redisdata:/data]

volumes: { pgdata: {}, redisdata: {} }
```

## 5 · Deploy em Render (staging)
1. Crie um banco Postgres na Render (Free tier).

2. Crie um serviço Web -> conecte repo Git, build command:

```bash
docker build -t backend .
```

start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

3. Adicione env vars via Dashboard (usar valores do .env).

4. Crie Cron Job (ex.: */6 * * * *) chamando python -m app.workers.fetch_prices.

5. Exponha URL pública — ficará algo como https://flighthunter-stg.onrender.com.

## 6 · Deploy em produção (AWS Fargate)
### (Blueprint ­— pode ser substituído por Heroku ou fly.io se preferir)

1. Infra (Terraform)
```bash
terraform init && terraform apply
```
### Recursos:
* VPC + 2 subnets (public/private)
* ALB + HTTPS (ACM cert)
* ECS Cluster + Fargate Service (task definition usa Docker img)
* RDS Postgres (db.t3.micro, Multi-AZ opcional)
* ElastiCache Redis (cache.t4g.micro)
* CloudWatch Log groups

2. CI/CD (GitHub Actions)
```yaml
- name: Build & Push
  uses: docker/build-push-action@v5
- name: Deploy to ECS
  uses: aws-actions/amazon-ecs-deploy-task-definition@v1
```

3. Secrets armazenados no AWS Secrets Manager, injetados via secrets: na task definition.

## 7 · Tarefas programadas
| Job             | Frequência    | Serviço                            | Notas                                |
| --------------- | ------------- | ---------------------------------- | ------------------------------------ |
| `fetch_prices`  | `*/6 * * * *` | Cron (Render) / ECS Scheduled Task | Chama Amadeus; grava `price_cache`.  |
| `send_alerts`   | `*/6 * * * *` | idem                               | Envia e-mails / Telegram se gatilho. |
| `cleanup_cache` | `0 3 * * *`   | idem                               | Remove preços >30 d.                 |

## 8. Observabilidade
| Ferramenta     | Endereço                           | Alerta                               |
| -------------- | ---------------------------------- | ------------------------------------ |
| **Sentry**     | `https://sentry.io/...`            | Erros 5xx → Slack                    |
| **Metabase**   | `https://metrics.flighthunter.app` | Alertas de 0 alertas enviados em 24h |
| **CloudWatch** | Logs ECS                           | Reboot container >3x/hr              |

## 9. 
* Render: manter último deploy disponível → botão “Rollback”.
* AWS: usar ECS CodeDeploy Blue/Green; tráfego 90/10 por 5 min antes de 100 %.

## 10. Checklist pós-deploy
 Endpoint /health retorna {"status":"ok"}.
 Stripe webhook test → 200 OK.
 Price fetch job grava registros em price_cache.
 Primeiro alerta de teste chega no seu e-mail.