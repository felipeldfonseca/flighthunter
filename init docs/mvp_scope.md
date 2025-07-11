# MVP Scope Doc — _“Flight Hunter”_  
_Version 0.1 • Draft • 09 Jul 2025_

---

## 1. Purpose  
Construir, em até **6 semanas**, um MVP funcional que:  

1. **Rastreia automaticamente** preços de passagens aéreas para rotas definidas pelo usuário.  
2. **Notifica** quando o preço cai abaixo do alvo ou varia -X %.  
3. Oferece **link de compra** em 1 clique usando **Duffel Links**, capturando markup/afiliado.  
4. Monetiza via **assinatura mensal** (Stripe) com plano Freemium ↔ Pro.  

Meta de aprendizado: validar disposição a pagar e colher feedback para o módulo de pacotes IA.

---

## 2. KPIs de sucesso  

| Métrica                    | Alvo MVP | Notas |
|----------------------------|----------|-------|
| **Pagantes ativos**        | ≥ 100    | Até T+90 d |
| **Retenção 30 d**          | ≥ 70 %   | % de usuários que receberam ≥1 alerta relevante |
| **Tempo de 1º alerta**     | ≤ 24 h   | Do cadastro ao push/email |
| **Erro crítico** (500/β)   | ≤ 1 %    | Logs de backend |

---

## 3. Personas‐chave  

1. **“Nômade Digital”** — voa 4-6×/ano, sensível a preço, usa Telegram.  
2. **“Caçador de Promo”** — segue canais de passagens, topa datas flexíveis.  

---

## 4. Funcionalidades (scope fechado)

| Categoria       | Must-have (MVP)                                   | Nice-to-have (deixar out) |
|-----------------|---------------------------------------------------|---------------------------|
| **Onboarding**  | Form simples: origem, destino, datas ±flexibilidade, preço-alvo, e-mail/Telegram | Login social |
| **Alertas**     | Scheduler que puxa cotações **Amadeus Self-Service API** 4×/dia; lógica de “price-drop” | Push mobile, WhatsApp |
| **Booking Link**| **Duffel Links** gerado on-demand, redireciona para checkout Duffel | Checkout próprio |
| **Payments**    | **Stripe Checkout**: Plano Free (2 alertas) / Pro (ilimitado) | Boleto / PIX direto |
| **Admin**       | Dashboard básico (pgAdmin + Metabase) p/ logs & métricas | Painel custom |
| **Suporte**     | FAQ + e-mail (Zendesk free) | Chatbot IA |

Tudo que não constar na coluna Must-have fica oficialmente _fora do MVP_.

---

## 5. User Stories prioritárias  

| ID | Tipo | Descrição | Pri |
|----|------|-----------|-----|
| US-01 | Usuário | “Quero cadastrar rota GRU → JFK e ser avisado quando o preço cair para R$ 2 500.” | P0 |
| US-02 | Sistema | Disparar e-mail/Telegram quando `price_current ≤ price_target` | P0 |
| US-03 | Usuário | “Quero clicar no alerta e comprar em 1 clique.” | P0 |
| US-04 | Admin   | Visualizar lista de erros >400 em tempo real | P1 |
| US-05 | Usuário | Fazer upgrade do Free para Pro sem suporte humano | P1 |

---

## 6. Arquitetura & Stack  

```plaintext
┌──────────────────────┐      price fetch (cron / Cloud Scheduler)
│   Postgres (RDS)     │<────────────────────────────┐
│  • users             │                             │
│  • watchlist         │           ┌──────────────┐  │
│  • price_cache       │  calls    │  FastAPI      │──┼─> SendGrid
└──────────────────────┘  (REST)   │  backend      │  └─> Telegram Bot API
                ▲                  └─────┬────────┘
                │                         │
   Stripe  <────┘                Duffel Links API

| Camada        | Ferramentas                                              |
| ------------- | -------------------------------------------------------- |
| Backend       | **Python 3.12 + FastAPI**, hosted on **Render**          |
| Data          | **PostgreSQL 16** (RDS Free Tier) + **Redis** para cache |
| Crawling      | **Amadeus Self-Service API** (flight-offers)             |
| Booking       | **Duffel Links** (no-IATA)                               |
| Notificação   | **SendGrid** (e-mail) • **Telegram Bot** (HTTP)          |
| Auth/Pagto    | **Stripe Checkout & Webhooks**                           |
| Observability | **Sentry** (errors) • **Metabase Cloud** (dashboards)    |

7. Data Model (simplificado)
users(id, email, plan, stripe_customer_id, tg_chat_id, created_at)
watchlist(id, user_id, origin, destination, date_from, date_to, price_target, created_at)
price_cache(id, watchlist_id, offer_id, price, currency, fetched_at)
alerts(id, watchlist_id, price, sent_at, channel)

8. Segurança & Compliance
* Todo tráfego externo via HTTPS/TLS 1.2+.
* Tokens das APIs em AWS Secrets Manager.
* Nenhum dado de cartão toca o nosso servidor (Stripe MoR).
* LGPD: consentimento explícito para comunicações; opção de opt-out em cada e-mail.

9. Cronograma (6 semanas)
| Semana | Entregáveis                                                   |
| ------ | ------------------------------------------------------------- |
| 1      | Repositório Git + CI/CD, contas Amadeus, Duffel, Stripe       |
| 2      | Esquema DB, endpoint `/watchlist`, seed data, webhook Stripe  |
| 3      | Job de cotação + lógica price-drop; e-mail alerta funcionando |
| 4      | Bot Telegram + template de mensagem + log de cliques          |
| 5      | Landing page marketing + checkout Free/Pro; testes de carga   |
| 6      | Beta fechado (20 users) → ajustes → **Go Live público**       |

10. Riscos & Mitigações
| Risco                               | Impacto            | Plano                                   |
| ----------------------------------- | ------------------ | --------------------------------------- |
| Limite gratuito Amadeus             | Falha em cotar     | Cache + fallback para Skyscanner scrape |
| Falsos positivos/negativos de preço | Perda de confiança | Threshold duplo (Δ% + preço absoluto)   |
| Account spam (Telegram)             | Bloqueio do bot    | Rate-limit por user\_id                 |


11. Fora do escopo MVP
* Sugestões de hotel/roteiro IA
* Push mobile nativo
* Integrações PIX/Boleto
* Suporte 24/7 via chat IA 
Esses itens entram na Fase 2 (Pacotes IA → 300 pagantes).

12. Glossário
* Duffel Links – URL que contém flight-offer e processa pagamento para nós.
* Plan Free – até 2 alertas simultâneos.
* Plan Pro – ilimitado, R$ 39/mês, 7 d trial.

Próximo passo: validar este escopo, criar repositório e agendar setup das APIs.

