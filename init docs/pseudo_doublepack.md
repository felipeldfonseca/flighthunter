# Pseudo-código — Agente “Pacote Duplo”  
_Versão 0.1 • foca no backend orchestration (LangChain / OpenAI function-calling)_  

> **Objetivo:** receber preferências do usuário e devolver JSON contendo  
> • `smart_saver` — pacote “econômico” (menor preço total)  
> • `comfort_plus` — pacote “premium” (➕ conforto, ≤ 1 escala, hotel ≥4⭐)  

---

## 1. Interfaces de função (esquema JSON resumido)

```jsonc
searchFlights(
  origin: string, destination: string,
  date_from: string, date_to: string,
  pax: int, cabin: string, max_results: int = 5
) -> [
  { "id": "...", "price": 2345.10, "currency": "BRL",
    "airlines": ["LA"], "stops": 1, "duration": "10h30" }
]

searchHotels(
  city: string, checkin: string, checkout: string,
  pax: int, max_results: int = 10
) -> [
  { "id": "...", "name": "Grand Hyatt",
    "price_nightly": 750.00, "currency": "BRL",
    "stars": 5, "rating": 8.9 }
]

composePackage(
  flight_id: string, hotel_id: string,
  nights: int, markup_pct: float
) -> {
  "package_price": 5320.00,
  "currency": "BRL",
  "duffel_link": "https://links.duffel.com/...",
  "hotel_affiliate_link": "https://apiss.amadeus.com/..."
}
```

```python
## 2. Orquestração (pseudo-código)
def build_duo_package(user_prefs):
    # --- 1. Busca de voos -----------------------------
    flights = searchFlights(
        origin=user_prefs.origin,
        destination=user_prefs.destination,
        date_from=user_prefs.date_from,
        date_to=user_prefs.date_to,
        pax=user_prefs.pax,
        cabin="ECONOMY",
        max_results=5
    )

    # Ordena pelo preço ascendente
    flights.sort(key=lambda f: f.price)

    # --- 2. Busca de hotéis ---------------------------
    hotels = searchHotels(
        city=user_prefs.destination_city,
        checkin=user_prefs.date_from,
        checkout=user_prefs.date_to,
        pax=user_prefs.pax,
        max_results=10
    )

    # Ordena por preço (asc) para Saver e por estrelas/nota para Plus
    hotels_by_price = sorted(hotels, key=lambda h: h.price_nightly)
    hotels_by_quality = sorted(hotels,
                               key=lambda h: (-h.stars, -h.rating, h.price_nightly))

    # --- 3. Seleção de combinações --------------------
    # Smart Saver: voo + hotel mais baratos que atendam orçamento
    saver_flight = flights[0]
    saver_hotel = hotels_by_price[0]

    # Comfort Plus: 1º voo <=1 escala + 1º hotel >=4 estrelas
    plus_flight = next(f for f in flights if f.stops <= 1)
    plus_hotel = hotels_by_quality[0]  # já garante ≥4⭐ pela ordenação

    # --- 4. Composição com markup ---------------------
    SAVER_MARKUP = 0.05   # 5 %
    PLUS_MARKUP  = 0.08   # 8 %

    saver_pkg = composePackage(
        flight_id=saver_flight.id,
        hotel_id=saver_hotel.id,
        nights=user_prefs.nights,
        markup_pct=SAVER_MARKUP
    )

    plus_pkg = composePackage(
        flight_id=plus_flight.id,
        hotel_id=plus_hotel.id,
        nights=user_prefs.nights,
        markup_pct=PLUS_MARKUP
    )

    # --- 5. Resposta final ----------------------------
    return {
        "query": {
            **user_prefs.dict()
        },
        "smart_saver": {
            "flight": saver_flight,
            "hotel": saver_hotel,
            **saver_pkg
        },
        "comfort_plus": {
            "flight": plus_flight,
            "hotel": plus_hotel,
            **plus_pkg
        }
    }
```

## 3. Fluxo para LangChain / Function-calling
1. System prompt instrui o LLM:
“Quando precisar de dados externos, invoque a função apropriada.”
2. LLM recebe user_prefs (preenchidos no onboarding).
3. Modelo decide:
→ searchFlights → → searchHotels → → composePackage
4. Última chamada retorna JSON final (conforme esquema).
5. Backend serializa e envia ao frontend/app.

## 4. Validações & regras de negócio
| Regra                                                                  | Enforced em                       |
| ---------------------------------------------------------------------- | --------------------------------- |
| Orçamento máximo (se definido) não pode ser excedido no *Smart Saver*. | check após composePackage         |
| “Comfort Plus” deve ter ≤1 escala e hotel ≥4⭐ ou rating ≥8.0.          | filtro antes de composePackage    |
| Markup variável por plano (Free vs Pro).                               | param `markup_pct`                |
| Sempre retornar na moeda de origem do usuário.                         | conversão via Amadeus FX endpoint |


## 5. Próximos passos
* Implementar mocks para searchFlights e searchHotels (tests unitários).
* Logar tempo de cada chamada API → monitorar performance.
* Definir retry/exponencial back-off em caso de falha de API.

Depois deste pseudo-código, partiremos para o prompt-template que guiará o LLM a seguir exatamente este fluxo.