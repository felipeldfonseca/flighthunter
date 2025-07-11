# Estrutura de Mensagem de Alerta ✈️  
_(para Telegram e e-mail)_  

## 1. Placeholders  

| Placeholder | Exemplo | Origem (tabela) |
|-------------|---------|-----------------|
| `{{ROUTE}}` | GRU → JFK | `watchlist.origin` + `destination` |
| `{{DATES}}` | 10 Nov 2025 – 24 Nov 2025 | `watchlist.date_from` + `date_to` |
| `{{PRICE_NOW}}` | R$ 2 345 | `price_cache.price` |
| `{{PRICE_TARGET}}` | R$ 2 500 | `watchlist.price_target` |
| `{{DELTA}}` | ↓ R$ 155 (-6,2 %) | calculado |
| `{{AIRLINES}}` | LATAM + Delta | da oferta |
| `{{STOPS}}` | 1 escala (ATL) | da oferta |
| `{{BOOK_LINK}}` | https://links.duffel.com/… | Duffel |
| `{{EXPIRES_IN}}` | 45 min | TTL calculado |

---

## 2. Template — **Telegram**  

```text
🔔 ✈️ Oferta encontrada {{ROUTE}}

💰 Agora: **{{PRICE_NOW}}**  
🎯 Seu alvo: {{PRICE_TARGET}}  
📉 Diferença: {{DELTA}}

📅 Datas: {{DATES}}  
👥 Cia(s): {{AIRLINES}} • {{STOPS}}

➡️ [Reservar agora]({{BOOK_LINK}})

⏳ Preço pode mudar em até {{EXPIRES_IN}}.  
Quer parar de receber alertas? /settings

* Botão inline único: “Reservar agora” (abre o BOOK_LINK).
* Segunda ação (opcional): “Ver outras datas” → deep-link p/ app/web.
```

3. Template — E-mail (plain-text)
Assunto: 🔔 [Flight Hunter] GRU → JFK por R$ 2 345 (abaixo do alvo!)
```text
Olá, {{FIRST_NAME}}!

Encontramos uma tarifa de **R$ 2 345** para o trecho **{{ROUTE}}** nas datas **{{DATES}}**, operada por {{AIRLINES}} ({{STOPS}}).

Isso está **{{DELTA}}** em relação ao seu objetivo de {{PRICE_TARGET}}.

Reserve em 1 clique:
{{BOOK_LINK}}

Observações:
• Tarifas e disponibilidade podem mudar rapidamente.
• Pagamento processado pela Duffel Ltd. — recibo imediato.
• Dúvidas? Basta responder este e-mail.

Bons voos!
Equipe Flight Hunter ✈️
```

Questionário de Onboarding 📝
| #  | Pergunta (pt-BR)                                        | Tipo UI                           | Campo/variável       | Obrigatório        |
| -- | ------------------------------------------------------- | --------------------------------- | -------------------- | ------------------ |
| 1  | **Cidade/ aeroporto de origem**                         | Autocomplete IATA                 | `origin`             | ✔                  |
| 2  | **Cidade/ aeroporto de destino**                        | Autocomplete IATA                 | `destination`        | ✔                  |
| 3  | **Data de ida**                                         | Date-picker                       | `date_from`          | ✔                  |
| 4  | **Data de volta**                                       | Date-picker                       | `date_to`            | ✔                  |
| 5  | **Flexibilidade** – quantos dias p/ +/-?                | Select (0 d • ±2 d • ±3 d • ±7 d) | `flex_days`          | ✔                  |
| 6  | **Preço-alvo (moeda local)**                            | Numeric                           | `price_target`       | ✔                  |
| 7  | **Nº de passageiros**                                   | Stepper                           | `pax_count`          | ✔                  |
| 8  | **Classe de cabine**                                    | Radio (Econ • Prem Econ • Biz)    | `cabin_class`        | ✖                  |
| 9  | **Companhias preferidas (opcional)**                    | Multi-select                      | `preferred_airlines` | ✖                  |
| 10 | **Canal de alerta**                                     | Toggle (E-mail • Telegram)        | `channel`            | ✔                  |
| 11 | **E-mail**                                              | Text                              | `email`              | obrig. se email    |
| 12 | **@Username Telegram**                                  | Text                              | `tg_chat_id`         | obrig. se Telegram |
| 13 | **Aceita receber ofertas de hotel quando disponíveis?** | Switch                            | `opt_in_hotels`      | ✖                  |


Observações de design
• Mantenha o formulário em 1 tela (mobile-first).
• Validar preço-alvo ≥ 50 % do preço médio histórico (evita alertas impossíveis).
• Coletar preferências opcionais já pavimenta o módulo de pacotes IA mais adiante.

Próximos passos imediatos
1. Implementar JSON de payload do watchlist conforme variáveis acima.
2. Construir templates handlebars / Jinja para as mensagens usando os placeholders.
3. Teste de usabilidade ⚡: 3 usuários cadastrando rota GRU → MIA; validar clareza do alerta.

