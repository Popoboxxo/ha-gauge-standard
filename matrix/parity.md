# Gauge Parity-Matrix (Pflegedatei)

Stand: 2026-10-06 · Kanon **v1.2** (`canon/entities.md`, Master = go_gauge 1.6.0) ·
Konvergenz-Ziel: command_gauge **1.0.0** (Kanon-Konvergenz vollzogen).

**Legende:** ✅ = Kanon erfüllt · ⚠️ = registrierte Abweichung (mit Kanon-ID und
Schließungsbedingung) · ❌ = unregistrierte Abweichung = Fehler · — = existiert
nicht (domain-seitig begründet).

Checker-Ergebnisse (Stand 2026-10-06):
`check_canon.py` → go_gauge: **0 Fehler / 0 Warnungen** (Referenz = grün) ·
command_gauge: **0 Fehler / 9 registrierte Warnungen** (Exit 0).

## Device-Topologie

| Aspekt | go_gauge | command_gauge | Status |
|---|---|---|---|
| Device pro Config-Entry `(DOMAIN, entry_id)` | ✅ `Go Gauge {ws}` | ✅ `Command Gauge {account}` | ✅ |
| manufacturer `Popoboxxo` | ✅ | ✅ | ✅ |
| model = API-Produktname | ✅ `OpenCode Go` | ✅ `CommandCode Cloud` | ✅ |
| Account-Device + Catalog-Owner | ✅ `Go Gauge Konto` | — (jeder Entry eigenes Konto) | ⚠️ CG-D1 (entfällt) |
| `_attr_has_entity_name`, kein `_attr_name`-Literal | ✅ | ✅ | ✅ |

## Fenster-Sensoren (7er-Satz, je Fenster)

| Entity (Kanon-Key) | go_gauge | command_gauge | Status |
|---|---|---|---|
| `usage` (% · MEASUREMENT · suffix `percent` · Status/Attribute) | ✅ | ✅ (`None` bei no_subscription/error, shield-off-Icon, Attribute) | ✅ |
| `reset` (TIMESTAMP) | ✅ | ✅ | ✅ |
| `forecast` (%, MEASUREMENT) | ✅ | ✅ | ✅ |
| `pace` (Ampel + Attribute) | ✅ | ✅ | ✅ |
| `remaining` (%) | ✅ | ✅ | ✅ |
| `time_to_reset` (DURATION, h) | ✅ | ✅ | ✅ |
| `burn_rate` (%/h) | ✅ | ✅ | ✅ |
| Fenster | ✅ 5h/week/month | ⚠️ 5h/week | ⚠️ CG-W1 (API) |

## Scope-Status (je Scope)

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `api_status` (ENUM-Ursache statt Ja/Nein) | ✅ (seit 1.6.0) | — (API: kein Scope-Status-Modell) | ⚠️ CG-B5 (API-blockiert) |

## Konto- / Katalog-Sensoren

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `model_catalog` (Key/Name/Suffix kanonisch) | ✅ | ✅ (Attribute `count`/`catalog_json`/`models_updated_at`) | ✅ |
| `model_catalog` Pricing-Attribute | ✅ | ⚠️ `live_count`/`free_models`/`cheapest_model`/`cheapest_overall`/`ranking_by_cost` fehlen | ⚠️ CG-C1 (API: kein Pricing) |
| `live_models_count` | ✅ | — | ⚠️ CG-C2 (API-blockiert) |
| `cheapest_model` | ✅ | — | ⚠️ CG-C2 |
| `free_models` | ✅ | — | ⚠️ CG-C2 |
| Credits (monthly/purchased/free/remaining) | — | ✅ (domain-erlaubt) | ✅ domain |
| Total cost / Requests / Tokens | — | ✅ (domain-erlaubt) | ✅ domain |
| `plan` | — | ✅ (domain-erlaubt) | ✅ domain |

## Binary Sensoren

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `rate_limited` (PROBLEM, je Fenster) | ✅ | ✅ | ✅ |
| `subscription_active` (kein device_class) | ✅ | ✅ | ✅ |
| `api_reachable` (konto-weit) | ✅ (Catalog Owner) | ✅ (`is_on` = `last_update_success` + `fetched_at`; bewusst immer `available`) | ✅ |
| `credits_below_threshold` | — | ✅ (domain-erlaubt) | ✅ domain CG-B4 |

## Settings

| Entity | go_gauge (Kanon) | command_gauge | Status |
|---|---|---|---|
| `warning_threshold` (% · 1–100 · `alert-octagon-outline`) | ✅ | ✅ | ✅ |
| `pace_red_limit` (% · `alert-decagram-outline`) | ✅ 1–300 | ⚠️ 1–1000 (domain: Forecast >300) | ⚠️ domain |
| `usage_refresh_min` (min · `timer-outline`) | ✅ 1–1440 | ⚠️ 5–1440 (Fair-Use) | ⚠️ domain |
| `models_refresh_min` (min · `timer-outline`) | ✅ 1–1440 | ⚠️ 60–1440 (Fair-Use) | ⚠️ domain |
| `auto_update_usage` / `auto_update_models` | ✅ | ✅ | ✅ |
| `refresh` (erzwingt beide Zyklen) | ✅ | ✅ | ✅ |

## Namen / Wortstellung

| Aspekt | go_gauge | command_gauge | Status |
|---|---|---|---|
| EN-Master, Fenster-Placeholder **vorn** (`{window} Usage`) | ✅ | ✅ | ✅ |
| `strings.json` + `translations/{en,de}.json` vollständig | ✅ | ✅ | ✅ |
| `Burn-Rate`-Schreibweise EN | ✅ | ✅ | ✅ |

## Verfahren (unverändert)

1. **Spiegelungs-Pflicht:** Jede Pattern-/Feature-Änderung an einer Integration
   wird im selben Arbeitsgang am Schwester-Repo geprüft und — soweit die API
   hergibt — gespiegelt (Paar-Change).
2. **Kanon zuerst:** Änderungen am Entity-Modell beginnen in
   `ha-gauge-standard` (Spec-first), dann Umsetzung in beiden Repos im selben
   Release-Zyklus.
3. **API-Differenzen dokumentieren, nicht verbiegen:** ⚠️-Eintrag mit
   Schließungsbedingung im Kanon; bei jedem Release auf „inzwischen
   umsetzbar?" prüfen.
4. **Naming parallel halten:** Coordinator-Attribute (`warn_percent`,
   `pace_red_percent`, `usage_minutes`, `models_minutes`, `auto_usage`,
   `auto_models`) sind bewusst identisch und bleiben es.
5. **Entity-Breaking = MAJOR** in dem Repo, in dem es passiert. command_gauge
   1.0.0 hat die Kanon-Keys übernommen; die Legacy-`unique_id`-Suffixe werden
   per Entity-Registry-Migration in-place umgeschrieben (Historie bleibt).
6. **Checker-Pflicht:** `scripts/check_canon.py` muss vor jedem Release gegen
   beide Repos grün laufen (Master: 0/0; Konvergenz-Ziel: 0 Fehler, nur
   registrierte ⚠️).

## Abweichungs-Index (⚠️-IDs)

| ID | Thema | Schließungsbedingung (Kurz) |
|---|---|---|
| CG-W1 | month-Fenster fehlt | CommandCode-API ergänzt Monatsfenster |
| CG-B5 | `api_status` fehlt | kein Scope-Status-Modell in der CommandCode-API |
| CG-C1 | Katalog-Pricing-Attribute fehlen | CommandCode-API liefert Pricing |
| CG-C2 | live/cheapest/free-Modelle fehlen | nur bei API-Erweiterung |
| CG-B4 | `credits_below_threshold` | domain-erlaubt, entfällt |
| CG-D1 | kein Account-Device/Catalog-Owner | entfällt (kein Duplikat-Problem) |
| — | Number-Ranges pace/usage/models | domain-begründet, entfällt |

**In v1.2 geschlossen (command_gauge 1.0.0):** CG-W2, CG-W3, CG-NAME1, CG-B1,
CG-B2, CG-B3, CG-N1 (Keys/Icons), CG-S1 — plus die vier Legacy-`unique_id`-Suffixe
(`usage`→`percent`, `exceeded`→`limited`, `models`→`model_catalog`,
`account_reachable`→`api_reachable`).

## Offene Punkte (beide Repos)

| ID | Punkt |
|---|---|
| OP-1 | `suggested_object_id`-Pinning auf Englisch (Vorbild `ha-health-o-mat`) — koordinierte Umsetzung + Registry-Migration geplant |
