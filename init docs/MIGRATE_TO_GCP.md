# MIGRATE_TO_GCP.md — Flight Hunter  
_Versão 0.1 • 10 Jul 2025_

> Migrar do SQLite local → **Cloud SQL for PostgreSQL 16**  
> usando créditos gratuitos (US$ 250) da sua conta Google Cloud.

---

## 1 · Arquitetura alvo

┌───────────────┐ https   ┌──────────────┐
│ Cloud Run     │◀───────▶│   Cloud SQL  │
│ (backend)     │         │ Postgres 16  │
└───────────────┘         └──────────────┘
      ▲                           ▲
      │ Ops / metrics             │ Backups auto, PITR
      ▼                           ▼
Cloud Logging             Cloud Monitoring


*Local dev* continua via Docker + **Cloud SQL Auth Proxy**.

---

## 2 · Estimativa de custo (us-central1)

| Recurso | Tipo | Qty | USD/mês |
|---------|------|-----|---------|
| Cloud SQL Postgres | **`db-f1-micro` (shared-core)** | 730 h | **≈ US$ 7,30** |
| Storage SSD | 10 GB | — | US$ 1,10 |
| Backups | 7 dias | inc. | ~US$ 0,50 |
| Cloud Run | 0,25 vCPU • 256 MB • 1 M req / mês | — | **≈ US$ 5,00** |
| **Total** | | | **≈ US$ 14 – 20 / mês** |

> ≈ 4 meses de uso com o crédito de US$ 250 se não crescer o tráfego.

---

## 3 · Pré-requisitos

```bash
gcloud components update
gcloud auth login
gcloud config set project <YOUR_PROJECT_ID>
```

Ative APIs:
```bash
gcloud services enable sqladmin.googleapis.com run.googleapis.com \
cloudbuild.googleapis.com
```

## 4 · Passo-a-passo
### 4.1 Criar instância Cloud SQL
```bash
gcloud sql instances create fh-postgres \
  --database-version=POSTGRES_16 \
  --cpu=1 --memory=3840MiB \
  --region=us-central1 --tier=db-f1-micro \
  --storage-size=10 --storage-type=SSD \
  --backup-start-time=03:00 --backup-enable
```

Criar banco & usuário:
```bash
gcloud sql users create fh_user --instance=fh-postgres --password='STRONG_PASS'
gcloud sql databases create flight_hunter --instance=fh-postgres
```

### 4.2 Exportar SQLite → Postgres (local)
```bash
# Dump schema + data do SQLite
sqlite3 flight.db .dump > dump.sql

# Ajustar dump: remover PRAGMA, alterar AUTOINCREMENT → SERIAL/BIGSERIAL
# (usar sed ou editar manualmente)

# Rodar proxy e psql
./cloud_sql_proxy -instances=<PROJECT>:us-central1:fh-postgres=tcp:5432 &
psql "host=127.0.0.1 user=fh_user dbname=flight_hunter password=STRONG_PASS" \
     -f dump.sql
```

### 4.3 Atualizar DATABASE_URL
No Secret Manager:
```ruby
postgresql://fh_user:STRONG_PASS@//cloudsql/<PROJECT>:us-central1:fh-postgres/flight_hunter
```

Adicione o secret ao Cloud Run:
Console → Cloud Run → Service → Variables & secrets → Add secret.

### 4.4 Deploy backend
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/fh-backend:latest
gcloud run deploy fh-backend \
  --image gcr.io/$PROJECT_ID/fh-backend:latest \
  --region us-central1 \
  --platform managed \
  --add-cloudsql-instances <PROJECT>:us-central1:fh-postgres \
  --set-secrets DATABASE_URL=projects/$PROJECT_ID/secrets/DATABASE_URL:latest \
  --allow-unauthenticated \
  --memory 512Mi --min-instances 0 --max-instances 2
```

(Min = 0 para hibernação → menor custo.)

### 4.5 Migrations & jobs
Depois do primeiro deploy:
```bash
gcloud run exec fh-backend --region us-central1 -- \
  alembic upgrade head
```

Agende cron jobs de fetch_prices e send_alerts via Cloud Scheduler → Pub/Sub → Cloud Run.

## 5 · Monitoramento & alertas
1. Cloud Monitoring → Metrics Explorer
    * database/cpu/utilization, database/disk/quota
2. Budget Alert
```bash
gcloud billing budgets create \
  --display-name="FH-budget" \
  --budget-amount=80 --threshold-rule=0.5 --threshold-rule=0.9
```
3. Log-based alert para erros 5xx do Cloud Run.

## 6 · Plano de rollback
| Etapa                | Ação                                                                                        |
| -------------------- | ------------------------------------------------------------------------------------------- |
| Falha em import SQL  | Restaurar dump SQLite, corrigir tipos, importar novamente                                   |
| Latência alta ou \$↑ | Reduzir `max_connections` no Cloud SQL (GUI)                                                |
| Crise de custo       | Alterar instância para `db-g1-small` (menos RAM) ou suspender Cloud Run (`min-instances=0`) |

## 7 · Futuro (pós-crédito)
1. Trocar para Always-Free Cloud SQL? (só MySQL no tier gratuito).
2. Migrar para Postgres em LightSail, Supabase ou Render basic.
3. Ou manter Cloud SQL e ativar plano de produção (mais RAM).

## Checklist “Done”
 Instância Cloud SQL criada & acessível.
 Dump importado sem erros.
 Backend em Cloud Run conectado via secret.
 CI atualizado (DATABASE_URL placeholder).
 Budget alerts configurados.