# Gauge Parity-Matrix (Pflegedatei)

Stand: 2026-10-15 · Kanon **v1.5.0** (`canon/entities.md`, Master = go_gauge 1.6.0) ·
Konvergenz-Ziel: command_gauge **1.2.0** (Kanon-Konvergenz + `api_status`, korrigiertes synthetisches Monatsfenster).

**Legende:** ✅ = Kanon erfüllt · ⚠️ = registrierte Abweichung (mit Kanon-ID und
Schließungsbedingung) · ❌ = unregistrierte Abweichung = Fehler · — = existiert
nicht (domain-seitig begründet).

Checker-Ergebnisse (Stand 2026-10-15):
`check_canon.py` → go_gauge: **0 Fehler / 0 Warnungen** (Referenz = grün) ·
command_gauge: **0 Fehler / 8 registrierte Warnungen** (Exit 0).

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
| Fenster | ✅ 5h/week/month (API) | ✅ 5h/week (API) + month **synthetisch** ⚠️ CG-M1 | ✅ |

## Scope-Status (je Scope)

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `api_status` (ENUM-Ursache statt Ja/Nein) | ✅ (seit 1.6.0) | ✅ (abgeleitet aus `section_status`/Abo/Fenster, seit 1.2.0) | ✅ |

## Config-Flow: Token-Erneuerung (Reauth)

Kanon §12 (neu in v1.5.0). command_gauge **1.2.0** ist die konforme
Referenzimplementierung (Reauth vollständig); go_gauge zieht mit **PR #32**
nach (noch offen). Status **✅ / kein ⚠️** — die Angleichung ist als Paar-Change
beschlossen, keine domain-begründete Divergenz.

| Aspekt (Kanon §12) | go_gauge | command_gauge | Status |
|---|---|---|---|
| 401 → `ConfigEntryAuthFailed` (typisierter Auth-Status, nicht transient) | ✅ (PR #32, offen) | ✅ (Referenz) | ✅ |
| 403 EntitlementError ≠ Auth (bleibt `no_subscription`) | ✅ | ✅ | ✅ |
| `async_step_reauth` → `async_step_reauth_confirm`, nur Secret ersetzt | ✅ (PR #32, offen) | ✅ (Referenz) | ✅ |
| `unique_id`/`entry_id` bleiben unverändert | ✅ | ✅ | ✅ |
| Setup re-raised `ConfigEntryAuthFailed` nach `hass.data`-Cleanup | ✅ (PR #32, offen) | ✅ (Referenz) | ✅ |
| i18n: `reauth_confirm` + Abort-Gründe in `strings.json`/`translations/*` | ✅ (PR #32, offen) | ✅ (Referenz) | ✅ |
| Kein `VERSION`-Bump / kein `async_migrate_entry` | ✅ | ✅ | ✅ |
| Status-Sensor bildet Auth strukturell ab (`auth_error`, §4) | ✅ | ✅ | ✅ |

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
| `pace_red_limit` (% · `alert-decagram-outline`) | ✅ 1–300 | ⚠️ 1–1000 (domain: Forecast >300) | ⚠️ CG-N2 |
| `usage_refresh_min` (min · `timer-outline`) | ✅ 1–1440 | ⚠️ 5–1440 (Fair-Use) | ⚠️ CG-N3 |
| `models_refresh_min` (min · `timer-outline`) | ✅ 1–1440 | ⚠️ 60–1440 (Fair-Use) | ⚠️ CG-N4 |
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
| CG-M1 | month-Fenster **synthetisch** (kein API-Fenster) | entfällt (dokumentiert); bei echtem API-Monatsfenster Synthese entfernen |
| CG-C1 | Katalog-Pricing-Attribute fehlen | CommandCode-API liefert Pricing |
| CG-C2 | live/cheapest/free-Modelle fehlen | nur bei API-Erweiterung |
| CG-B4 | `credits_below_threshold` | domain-erlaubt, entfällt |
| CG-D1 | kein Account-Device/Catalog-Owner | entfällt (kein Duplikat-Problem) |
| CG-N2 | `pace_red_limit` Range 1–1000 | domain-begründet, entfällt |
| CG-N3 | `usage_refresh_min` Min 5 | domain-begründet (Fair-Use), entfällt |
| CG-N4 | `models_refresh_min` Min 60 | domain-begründet (Fair-Use), entfällt |

**In v1.4.0 (command_gauge 1.2.0):** `api_status` implementiert — die Abweichung
**CG-B5** ist geschlossen. Der Kanon-Enum wird aus dem Per-Sektion-Status
(`section_status`), dem Abo-Status und den Fenster-`exceeded`-Flags abgeleitet
(401 → `auth_error`, inaktives Abo → `no_subscription`, sonstiger Sektionsfehler
→ `api_error`, überschrittenes Fenster → `rate_limited`, sonst `ok`).

**In v1.3.1 (command_gauge 1.1.1):** Die synthetische `month`-Ableitung (⚠️
CG-M1) wurde korrigiert — `cap` = Plan-Grant (Plan-Katalog, gekeyt über `planId`),
`used = max(0, cap − credits.monthly_credits)`, `reset = subscription.period_end`.
`credits.monthlyCredits` ist ein Rest-Betrag, kein Grant; die 1.1.0-Ableitung
(`cap=monthly_credits`, `used=summary.total_cost`) ließ den Prozentwert mit
schwindendem Grant steigen.

**In v1.3 (command_gauge 1.1.0):** `month`-Fenster synthetisch ergänzt
(7er-Satz + `rate_limited`); die frühere `windows`-Abweichung entfällt, da die
Fenster-Reihenfolge jetzt kanonisch ist.

**In v1.2 geschlossen (command_gauge 1.0.0):** CG-W2, CG-W3, CG-NAME1, CG-B1,
CG-B2, CG-B3, CG-N1 (Keys/Icons), CG-S1 — plus die vier Legacy-`unique_id`-Suffixe
(`usage`→`percent`, `exceeded`→`limited`, `models`→`model_catalog`,
`account_reachable`→`api_reachable`).

## Offene Punkte (beide Repos)

| ID | Punkt |
|---|---|
| OP-1 | `suggested_object_id`-Pinning auf Englisch (Vorbild `ha-health-o-mat`) — koordinierte Umsetzung + Registry-Migration geplant |
