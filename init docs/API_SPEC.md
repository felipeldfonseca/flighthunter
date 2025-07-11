# API_SPEC.md — Flight Hunter  
_OpenAPI 3.1 • Draft 0.1 • 10 Jul 2025_

> **Scope:** endpoints expostos pelo backend FastAPI no MVP (alertas de voo, Stripe billing).  
> **Base URL (prod):** `https://api.flighthunter.app/v1`

---

## 1 · Resumo dos endpoints

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/watchlist` | Criar rota monitorada pelo usuário | Bearer (JWT) |
| `GET`  | `/watchlist` | Listar rotas do usuário | Bearer |
| `GET`  | `/watchlist/{id}` | Detalhe de uma rota | Bearer |
| `DELETE` | `/watchlist/{id}` | Remover rota | Bearer |
| `POST` | `/stripe/webhook` | Receber eventos Stripe (checkout, invoice) | Assinatura Stripe |
| `GET`  | `/health` | Health-check simples | — |

---

## 2 · Componentes de esquema (YAML)

```yaml
components:
  schemas:
    WatchlistCreate:
      type: object
      required: [origin, destination, date_from, date_to, price_target, channel]
      properties:
        origin:        { type: string, example: "GRU" }
        destination:   { type: string, example: "JFK" }
        date_from:     { type: string, format: date, example: "2025-11-10" }
        date_to:       { type: string, format: date, example: "2025-11-24" }
        flex_days:     { type: integer, minimum: 0, maximum: 7, example: 2 }
        price_target:  { type: number, format: float, example: 2500.00 }
        pax:           { type: integer, default: 1, example: 2 }
        cabin_class:   { type: string, enum: [ECONOMY, PREMIUM_ECONOMY, BUSINESS], default: ECONOMY }
        channel:       { type: string, enum: [EMAIL, TELEGRAM] }
        tg_chat_id:    { type: string, nullable: true, example: "123456789" }
    Watchlist:
      allOf:
        - $ref: "#/components/schemas/WatchlistCreate"
        - type: object
          properties:
            id:        { type: string, format: uuid }
            created_at:{ type: string, format: date-time }
    Alert:
      type: object
      properties:
        id:        { type: string, format: uuid }
        watchlist_id: { type: string, format: uuid }
        price:     { type: number, format: float }
        currency:  { type: string, example: "BRL" }
        sent_at:   { type: string, format: date-time }
        channel:   { type: string, enum: [EMAIL, TELEGRAM] }
    Error:
      type: object
      required: [detail]
      properties:
        detail:    { type: string }
```

## 3 · Detalhamento de endpoints
### 3.1 POST /watchlist
|                  |                                                                      |
| ---------------- | -------------------------------------------------------------------- |
| **Desc.**        | Cadastra nova rota a ser monitorada.                                 |
| **Auth**         | *Bearer* (JWT gerado pós-login Stripe Customer Portal / Magic Link). |
| **Request body** | `WatchlistCreate`                                                    |
| **Response 201** | `Watchlist`                                                          |
| **Erros**        | `400` dados inválidos • `409` rota duplicada                         |

### Exemplo de request:
```jsonc
POST /watchlist
Authorization: Bearer <token>

{
  "origin": "GRU",
  "destination": "JFK",
  "date_from": "2025-11-10",
  "date_to": "2025-11-24",
  "flex_days": 2,
  "price_target": 2500.00,
  "pax": 2,
  "channel": "EMAIL"
}
```
### Exemplo de resposta:
```jsonc
HTTP/1.1 201 Created
{
  "id": "6b1566fb-dd32-46b1-ae80-3c7f5e8e1198",
  "origin": "GRU",
  "destination": "JFK",
  "date_from": "2025-11-10",
  "date_to": "2025-11-24",
  "flex_days": 2,
  "price_target": 2500.0,
  "pax": 2,
  "cabin_class": "ECONOMY",
  "channel": "EMAIL",
  "tg_chat_id": null,
  "created_at": "2025-07-10T14:25:31Z"
}
```

### 3.2 GET /watchlist
|                  |                                           |
| ---------------- | ----------------------------------------- |
| **Desc.**        | Retorna todas as rotas do usuário logado. |
| **Query params** | `page`, `size` (paginação simples).       |
| **Response 200** | `array<Watchlist>`                        |

### 3.3 GET /watchlist/{id}
|                  |                                                                   |
| ---------------- | ----------------------------------------------------------------- |
| **Desc.**        | Retorna detalhes de uma rota específica (inclui últimos alertas). |
| **Response 200** | objeto: `{ watchlist: Watchlist, alerts: array<Alert> }`          |
| **Erros**        | `404` não encontrado (ou não pertence ao usuário)                 |

### 3.4 DELETE /watchlist/{id}
|                  |                                         |
| ---------------- | --------------------------------------- |
| **Desc.**        | Remove rota e desativa alertas futuros. |
| **Response 204** | Sem corpo.                              |

### 3.5 POST /stripe/webhook
|              |                                                                    |
| ------------ | ------------------------------------------------------------------ |
| **Desc.**    | Recebe eventos de checkout, pagamento e atualização de assinatura. |
| **Security** | Validação de assinatura (`Stripe-Signature` header).               |
| **Body**     | Objeto `StripeEvent` (deserializado pela lib Stripe Python).       |
| **Resposta** | `200` texto “ok” ou `400` se assinatura inválida.                  |

### Eventos usados:
checkout.session.completed, invoice.payment_succeeded, customer.subscription.updated, customer.subscription.deleted.

### 3.6 GET /health
|                  |                                                           |
| ---------------- | --------------------------------------------------------- |
| **Desc.**        | Retorna “pong” para monitoramento Kubernetes/Render.      |
| **Response 200** | `{ "status": "ok", "timestamp": "2025-07-10T14:30:00Z" }` |

## 4 · Códigos de erro padrão
| HTTP  | Motivo                                  | Corpo                               |
| ----- | --------------------------------------- | ----------------------------------- |
| `400` | Validação / formato inválido            | `{ "detail": "BAD_REQUEST" }`       |
| `401` | Token ausente ou expirado               | `{ "detail": "UNAUTHORIZED" }`      |
| `404` | Recurso não encontrado                  | `{ "detail": "NOT_FOUND" }`         |
| `409` | Conflito (já existe watchlist idêntica) | `{ "detail": "CONFLICT" }`          |
| `429` | Rate-limit excedido                     | `{ "detail": "TOO_MANY_REQUESTS" }` |
| `500` | Erro interno                            | `{ "detail": "INTERNAL_ERROR" }`    |

## 5 · Change-log
| Data       | Versão    | Alteração         |
| ---------- | --------- | ----------------- |
| 2025-07-10 | 0.1 draft | Documento inicial |

# Nota: Spec gerada automaticamente pelo FastAPI em /docs. Este arquivo serve como referência humana e base para testes de contrato.
