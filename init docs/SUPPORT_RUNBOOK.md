# SUPPORT_RUNBOOK.md — Flight Hunter  
_Versão 0.1 • 10 Jul 2025_

> Guia operacional para resolver tickets, reembolsos e incidentes  
> nos primeiros **1 000 usuários pagantes** (time de suporte = você + bots).

---

## 1 · Canais oficiais

| Canal | Uso | SLA externo |
|-------|-----|-------------|
| **E-mail** `support@flighthunter.app` | Todo tipo de solicitação | 12 h úteis |
| **Telegram Bot** `/help` | Perguntas rápidas, status de rota | 2 h úteis |
| **Status Page** `status.flighthunter.app` | Incidentes gerais | — |

*(Todos os tickets encaminhados ao **Zendesk**; ID = `FH-{yyyyMMdd}-{###}`)*

---

## 2 · Ferramentas & credenciais

| Ferramenta | Login | Função |
|------------|-------|--------|
| **Zendesk** | Google SSO | Gestão de tickets, macros |
| **Stripe Dashboard** | email corp. | Assinaturas, reembolsos, chargebacks |
| **Duffel Dashboard** | email corp. | Detalhes de reserva, reemissão ou cancelamento |
| **Amadeus Self-Service** | API key | Logs de busca |
| **Sentry** | GitHub SSO | Erros de app |
| **Metabase** | GitHub SSO | Logs de alertas, métricas NPS |

---

## 3 · Matriz de severidade & SLA interno

| Severidade | Exemplo | SLA de 1ª resposta | SLA de solução |
|------------|---------|--------------------|----------------|
| **S0** | Sistema fora do ar (500), múltiplos usuários | 15 min | 2 h |
| **S1** | Link de compra gera erro 400 / Stripe down | 1 h | 6 h |
| **S2** | Usuário não recebeu alerta esperado | 4 h | 24 h |
| **S3** | Pergunta geral, feature request | 12 h | 72 h |

---

## 4 · Macros de resposta (Zendesk)

### 4.1 “Alerta não recebido”
```text
Oi {{first_name}},

Verificamos que seu alerta para {{route}} está ATIVO e o último preço
consultado foi {{price}} às {{timestamp}}.

Lembre-se de que enviamos avisos somente quando o preço fica abaixo do
seu alvo de R$ {{target}} ou cai mais de 5 % em 24 h.

Se quiser ajustar preço-alvo ou datas, clique em Gerenciar alerta.

Qualquer dúvida, fico à disposição!
— Equipe Flight Hunter
```

### 4.2 “Reembolso/Cancelamento”
```text
Olá {{first_name}},

Seu pedido de cancelamento foi registrado. Segue o fluxo:

Solicitamos o cancelamento à companhia aérea via Duffel (#{{duffel_id}}).

Em até 48 h você receberá e-mail confirmando o valor reembolsado.

Stripe processará o crédito no seu cartão em 5–10 dias úteis.

Acompanhe o status neste link: {{status_url}}.

Atenciosamente,
Equipe Flight Hunter
```

---

## 5 · Procedimentos passo-a-passo

### 5.1 Reemissão por mudança de voo (Tier 1)

1. Recebe ticket “Flight time changed / need new connection”.  
2. No **Duffel Dashboard** → Reserva → botão **Change flights**.  
3. Escolher opção sem custo ou menor custo (≤R$100).  
4. Duffel gera nova e-ticket; enviar macro “Re-issued” + PDF ao usuário.  
5. Fechar ticket como **Solved** (tag `reemission`).

### 5.2 Reembolso & chargeback (Tier 2)

| Passo | Ferramenta |
|-------|------------|
| 1. Validar identidade (últimos 4 dígitos do cartão) | Zendesk macro |
| 2. Iniciar **Refund** no Stripe (`Payments → Refund`) | Stripe |
| 3. Notar valor e motivo (`duplicate`, `customer_request`, etc.) | Stripe |
| 4. Adicionar nota interna no ticket | Zendesk |
| 5. Duffel: cancelar reserva se <24 h da partida | Duffel |
| 6. Fechar ticket, tag `refund_done` | Zendesk |

*(Chargeback abriu? -> juntar logs de alerta, email, IP e responder no Stripe
dentro 7 dias.)*

### 5.3 Falha de pagamento Stripe

1. Webhook `invoice.payment_failed` dispara Sentry breadcrumb.  
2. Ticket automático criado (type `billing`).  
3. Enviar macro “Atualizar cartão” (link para Customer Portal).  
4. Se 3 tentativas falharem (d-9), setar plano `FREE`.

### 5.4 Incidente S0 (API down)

1. PagerDuty → telefone.  
2. `status.flighthunter.app` → Set status _Major Outage_.  
3. Rollback última deploy via Render or ECS.  
4. Post-mortem em 24 h (template `incident_template.md`).

---

## 6 · Checklist semanal

| Dia | Tarefa | Ferramenta |
|-----|--------|-----------|
| Seg | Verificar `price_fetch` logs de falha > 1 % | Metabase |
| Qua | Conferir chargebacks pendentes | Stripe |
| Sex | Exportar `alerts` enviados → KPI semanal (WAU, % sucesso) | Metabase |
| Sex | Teste manual: criar rota dummy GRU→MIA | API / Bot |

---

## 7 · Métricas de suporte

* **Ticket volume / 1 000 users** (meta < 15)  
* **Tempo médio 1ª resposta** (meta < 2 h)  
* **Taxa de reembolso** (< 2 %)  
* **CSAT** (em macro de resolução) → meta ≥ 4,6/5

---

## 8 · Contatos de escalonamento

| Área | Nome | Slack | Backup |
|------|------|-------|--------|
| Tech Lead | Felipe (você) | `@felipe` | n/a |
| Duffel Support | NOC Duffel | support@duffel.com | — |
| Stripe | Stripe Emergencies | +1-888-555-1234 | — |

---

> **Sempre documente** qualquer exceção de voo ou reembolso no ticket.  
> Elimine tribal knowledge: atualize este runbook após cada incidente novo!


