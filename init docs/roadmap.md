# 🗺️ ROADMAP.md — Visão Longo-Prazo • Flight Hunter  
_Ult. atualização: 09 Jul 2025_

> **Missão:** Eliminar o atrito de planejar e reservar viagens, oferecendo um agente 100 % automatizado que encontra, recomenda, reserva e monitora cada etapa — sempre na melhor relação custo-benefício para o usuário.

---

## 📈 Visão em Camadas

| Horizonte | Bloco de valor principal | O que o usuário percebe | Capabilidades internas necessárias |
|-----------|--------------------------|-------------------------|------------------------------------|
| **H-0** (Hoje) | ⚡ **Alertas de preço + Compra 1-clique** | “Me avise quando meu voo cair de preço e deixe-me comprar na hora.” | Scraper/APIs de voo, Duffel Links, Stripe Billing |
| **H-1** (6-12 m) | 🏷️ **Pacotes IA Dinâmicos** | Dois pacotes montados sob medida (Smart Saver / Comfort Plus) com voo + hotel prontos para check-out único | Motor de roteirização IA, afiliados de hotel, pricing rule-engine |
| **H-2** (12-24 m) | 🚄 **Multimodal & Pós-compra** | Voos, trens, ônibus, carro, seguro — monitorados e reemitidos automaticamente se algo der errado | Integrações Rome2Rio, CarTrawler; back-office de reemissão; time de operações |
| **H-3** (24-36 m) | 🤖 **Concierge 24/7 “Fale & Viaje”** | Planejar ou alterar viagem inteiro via chat/voz (Web, App, WhatsApp, Copilot) | LLMs com **function calling**, voicebot Twilio, pipeline de LUI (language → intent) |
| **H-4** (36-60 m) | 💳 **Fintech & Fidelidade** | Cartão/bank-as-a-service com cashback em milhas, BNPL, proteção de preço pós-compra | Licença MoR completa, partnerships bancárias, motor de risco, programa de pontos |
| **H-5** (5 + anos) | 🌍 **Marketplace de Experiências + API Platform** | Reservar passeios locais e oferecer nossa “máquina” de pacotes IA a OTAs e bancos via API | Curadoria local (supply), _white-label_ API, portal de devs, SSO corporativo |

---

## 🔢 Macro-marcos & KPIs

| Ano fiscal | GMV alvo | Receita alvo | Usuários pagantes | OKR “North Star” |
|------------|----------|--------------|-------------------|------------------|
| 2025 | R$ 8 M | R$ 1 M | 1 000 | **Time-to-alert < 4 h** |
| 2026 | R$ 60 M | R$ 8 M | 10 000 | **NPS > 55** |
| 2027 | R$ 220 M | R$ 30 M | 50 000 | **% de reservas 100 % self-service ≥ 60 %** |
| 2028 | R$ 700 M | R$ 100 M | 200 000 | **LTV/CAC ≥ 5** |
| 2030 | R$ 3 B | R$ 350 M | 1 M | **Margem bruta  ≥  65 %** |

---

## 📅 Cronograma Detalhado

### Fase 0 — _MVP Alpha_ (Q3 / 2025)  
* **Done:** arquitetura básica, Amadeus crawler, Duffel Links, Stripe.  
* **Meta:** 100 clientes pagantes (Free→Pro).

### Fase 1 — _Pacotes IA & Hotels_ (Q4 / 2025)  
- Integrar Amadeus Hotel Search → pilotar markup de 10 %.  
- **Agente IA v1** (LangChain) gera 2 pacotes.  
- Lançar **checkout único** (Duffel Payments).  
- **Contratar** 1 UX designer PT 20 h.

### Fase 2 — _App & IATA Lite_ (H1 / 2026)  
- React Native app + push FCM.  
- Registrar **TIDS** (IATA) para comissões hotel.  
- Configurar **Metabase Cloud** dashboards.  
- OKR: **Retenção 30d ≥ 70 %**.

### Fase 3 — _Multimodal & Ops_ (H2 / 2026)  
- APIs: Rome2Rio (trem/bus), CarTrawler (car).  
- **Back-office reemissão** (Zapier-driven + 1 analista Ops).  
- Suporte SLA < 2 h.  
- **Seed round US$ 2-4 M**.

### Fase 4 — _Concierge 24-7_ (2027)  
- Twilio voicebot, WhatsApp Business Cloud.  
- **LLM router** decide ação (voo, hotel, cancelamento).  
- Metrics: **% tickets resolvidos sem humano ≥ 50 %**.  
- **Hiring:** CTO ≠ founder (você vira Chief Product), 1 ML lead.

### Fase 5 — _Fintech & Loyalty_ (2028)  
- **Card-as-a-Service** (Dock / Marketa) com cashback.  
- Motor **price-drop refund** automático (Google Flights-like).  
- BNPL via parc. mercado local (Mercado Pago, Nubank).  
- GMV run-rate > R$ 700 M.

### Fase 6 — _Platformization_ (2029-2030)  
- Expor **API de pacotes IA** a bancos digitais & OTAs regionais.  
- **Marketplace de experiências** (ingressos, tours) com rev-share 20 %.  
- **Series B+** (if needed) para expansão EMEA / APAC.

---

## 🏗️ Escalada Técnica

1. **Micro-services** via FastAPI + gRPC quando >50 req/s.  
2. **Event Bus** (Kafka) para price-updates e webhooks (fan-out).  
3. **Data Lakehouse** (BigQuery) → painel de _fare trends_, alimentar ML de predição.  
4. **LLM infra BYO**: fine-tune nos nossos dados, evitar lock-in.  
5. **Chaos & Load tests** trimestrais.

---

## 👥 Hiring Plan

| Faixa de usuários | Funções críticas | Total headcount |
|-------------------|------------------|-----------------|
| 0–1 000 | Founder-solo + part-time designer | 2 |
| 1 000–10 000 | Ops Analyst, SEO Growth, Full-stack | 5-6 |
| 10 000–50 000 | ML Lead, Mobile dev, Support Lead | 10-12 |
| 50 000 + | Fintech PM, Compliance, DataSci | 20 + |

---

## ⚖️ Compliance & Risco

| Marco | Reg. | Ação |
|-------|------|------|
| TIDS | IATA | Concluído F1 / 2026 |
| PCI-DSS SAQ A | Cartão | Stripe MoR mantém; re-auditar a cada 12 m |
| LGPD/GDPR | Dados | DPO part-time, mapeamento PIA |
| PSD2 & Open Banking | Fintech | Parceria banco-custodiante 2028 |

---

## 💰 Degraus de Funding

| Round | Trigger | Uso principal | Múltiplo-alvo |
|-------|---------|---------------|---------------|
| **Pre-Seed (Angel)** | MVP live, 100 pag. | Infra + marketing orgânico | 3-5 × ARR |
| **Seed (~US$ 3 M)** | 1 K pag., 100 K MRR | IATA + App + Ops | 5-8 × ARR |
| **Series A (~US$ 10 M)** | 10 K pag., GMV ≥ R$ 60 M | Multimodal + LatAm ads | 6-10 × |
| **Series B+** | 200 K pag., GMV ≥ R$ 700 M | Fintech + global | 4-6 × |

---

## 🧭 North-Star KPI Framework

1. **Usuários Ativos Semanais (WAU)**  
2. **Alertas Relevantes Entregues / WAU**  
3. **Reservas 1-Clique / Alerta**  
4. **GMV por Usuário**  
5. **Margem Bruta (%)**  

Revisar quarterly; cada feature só entra se melhorar ≥ 1 KPI core.

---

## 🌱 Cultura & Princípios

* **Focus on leverage:** automatizar antes de contratar.  
* **Data > HiPPO:** decisões de rota e preço dirigidas por analytics.  
* **Privacy-first:** coleta mínima, cifrada de ponta-a-ponta.  
* **Fail forward:** iterar, publicar changelog público.  

---

> *Este roadmap é vivo e revisto a cada Q. Contribuições e pull requests com melhorias são bem-vindas.*
