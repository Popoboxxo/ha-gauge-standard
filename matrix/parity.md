# Gauge Parity-Matrix (Pflegedatei)

Stand: 2026-10-27 · Kanon **v1.8.0** (`canon/entities.md`, Master = go_gauge **2.1.0**,
Konto-ConfigEntry + `account_`-Präfix, Burn-Lookback aktiviert; zusätzlich
Repository-Hygiene `canon/repository.md` v1.7.0, Hygiene-Referenz go_gauge
**2.0.2**) ·
Konvergenz-Ziel: command_gauge **1.2.0** (Kanon-Konvergenz + `api_status`, korrigiertes synthetisches Monatsfenster).

**Legende:** ✅ = Kanon erfüllt · ⚠️ = registrierte Abweichung (mit Kanon-ID und
Schließungsbedingung) · ❌ = unregistrierte Abweichung = Fehler · — = existiert
nicht (domain-seitig begründet).

Checker-Ergebnisse (Stand 2026-10-26):
`check_canon.py` → go_gauge: **0 Fehler / 0 Warnungen** (Referenz = grün) ·
command_gauge: **15 registrierte Warnungen**, **0 Fehler** — die D22-Diagnose-
Attribute (`forecast`, `pace`, `burn_rate`) sind als ⚠️ CG-C3 registriert, bis
der Paar-Change in command_gauge sie liefert.

## Device-Topologie

| Aspekt | go_gauge | command_gauge | Status |
|---|---|---|---|
| Device pro Config-Entry `(DOMAIN, entry_id)` | ✅ `Go Gauge {ws}` | ✅ `Command Gauge {account}` | ✅ |
| manufacturer `Popoboxxo` | ✅ | ✅ | ✅ |
| model = API-Produktname | ✅ `OpenCode Go` | ✅ `CommandCode Cloud` | ✅ |
| Account-Device | ✅ `Go Gauge Konto`, owned by der **eigenen Konto-ConfigEntry** (`entry_kind: "account"`, `unique_id: go_gauge_account`) — **kein Catalog Owner** | — (jeder Entry eigenes Konto) | ⚠️ CG-D1 (Doku-Info, entfällt) |
| `_attr_has_entity_name`, kein `_attr_name`-Literal | ✅ | ✅ | ✅ |

## Fenster-Sensoren (7er-Satz, je Fenster)

| Entity (Kanon-Key) | go_gauge | command_gauge | Status |
|---|---|---|---|
| `usage` (% · MEASUREMENT · suffix `percent` · Status/Attribute) | ✅ | ✅ (`None` bei no_subscription/error, shield-off-Icon, Attribute) | ✅ |
| `reset` (TIMESTAMP) | ✅ | ✅ | ✅ |
| `forecast` (%, MEASUREMENT) | ✅ + D22-Attribute | ✅ (ohne D22-Attribute: ⚠️ CG-C3) | ⚠️ CG-C3 |
| `pace` (Ampel + Attribute) | ✅ + D22-Attribute | ✅ (ohne D22-Attribute: ⚠️ CG-C3) | ⚠️ CG-C3 |
| `remaining` (%) | ✅ | ✅ | ✅ |
| `time_to_reset` (DURATION, h) | ✅ | ✅ | ✅ |
| `burn_rate` (%/h) | ✅ (OLS + Lookback-Attribute) | ✅ (ohne Lookback-Attribute: ⚠️ CG-C3) | ⚠️ CG-C3 |
| Fenster | ✅ 5h/week/month (API) | ✅ 5h/week (API) + month **synthetisch** ⚠️ CG-M1 | ✅ |

## Scope-Status (je Scope)

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `api_status` (ENUM-Ursache statt Ja/Nein) | ✅ (seit 1.6.0) | ✅ (abgeleitet aus `section_status`/Abo/Fenster, seit 1.2.0) | ✅ |

## Config-Flow: Token-Erneuerung (Reauth)

Kanon §12 (neu in v1.5.0). command_gauge **1.2.0** ist die konforme
Referenzimplementierung (Reauth vollständig); go_gauge zieht mit **PR #32**
nach (gemergt 2026-10-18). Status **✅ / kein ⚠️** — die Angleichung ist als Paar-Change
beschlossen, keine domain-begründete Divergenz.

| Aspekt (Kanon §12) | go_gauge | command_gauge | Status |
|---|---|---|---|
| 401 → `ConfigEntryAuthFailed` (typisierter Auth-Status, nicht transient) | ✅ (PR #32, gemergt) | ✅ (Referenz) | ✅ |
| 403 EntitlementError ≠ Auth (bleibt `no_subscription`) | ✅ | ✅ | ✅ |
| `async_step_reauth` → `async_step_reauth_confirm`, nur Secret ersetzt | ✅ (PR #32, gemergt) | ✅ (Referenz) | ✅ |
| `unique_id`/`entry_id` bleiben unverändert | ✅ | ✅ | ✅ |
| Setup re-raised `ConfigEntryAuthFailed` nach `hass.data`-Cleanup | ✅ (PR #32, gemergt) | ✅ (Referenz) | ✅ |
| i18n: `reauth_confirm` + Abort-Gründe in `strings.json`/`translations/*` | ✅ (PR #32, gemergt) | ✅ (Referenz) | ✅ |
| Kein `VERSION`-Bump / kein `async_migrate_entry` | ✅ | ✅ | ✅ |
| Status-Sensor bildet Auth strukturell ab (`auth_error`, §4) | ✅ | ✅ | ✅ |

## Konto-ConfigEntry (go_gauge 2.0.0, Kanon §13)

go_gauge besitzt **eine** workspace-unabhängige Konto-Entry
(`entry_kind: "account"`, `unique_id: go_gauge_account`, Device
`Go Gauge Konto` mit `identifiers: {(DOMAIN, "account")}`). Konto-Entities
tragen das `unique_id`-Präfix `account_`. command_gauge hat keine
Konto-Entry (**1 Entry = 1 Konto**) und bildet die Entities auf seiner eigenen
Entry ab — kein Konto-Split (Kanon §13.3).

| # | Entity | Plattform | unique_id | go_gauge | command_gauge | Status |
|---|---|---|---|---|---|---|
| 1 | Model Catalog | sensor | `account_model_catalog` | ✅ | ✅ (eigene Entry) | ✅ |
| 2 | Live Models Count | sensor | `account_models_live_count` | ✅ | — | ⚠️ CG-C2 |
| 3 | Cheapest Model | sensor | `account_cheapest_model` | ✅ | — | ⚠️ CG-C2 |
| 4 | Free Models | sensor | `account_free_models` | ✅ | — | ⚠️ CG-C2 |
| 5 | API Reachable | binary_sensor | `account_api_reachable` | ✅ (Evidenz/TTL) | ✅ (`last_update_success` + `fetched_at`) | ✅ |
| 6 | Refresh | button | `account_refresh` | ✅ (nur Katalog-Fetch) | ✅ (eigene Entry) | ✅ |
| 7 | Auto Update Models | switch | `account_auto_update_models` | ✅ (global, Default ON) | ✅ (eigene Entry) | ✅ |
| 8 | Models Refresh (min) | number | `account_models_refresh_minutes` | ✅ (global, 1–1440, Default 60) | ⚠️ 60–1440 (Fair-Use) | ⚠️ CG-N4 |

Migration (go_gauge, Kanon §13.2): `VERSION` 8 setzt `entry_kind`; `entity_id`
und History bleiben erhalten; die `unique_id`-Umschreibung erfolgt im
Adoption-Sweep (`account_*`, Konto-Entry + Konto-Device); die vormaligen
Workspace-Modell-Settings (`*_auto_update_models`,
`*_models_refresh_minutes`) werden aus der Registry entfernt. HA-Minimum
**2026.8.0**, Integration `version` **2.0.0**.

## Konto- / Katalog-Sensoren

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `model_catalog` (Key/Name/Suffix kanonisch) | ✅ (Konto-Entry, `account_`-Präfix) | ✅ (Attribute `count`/`catalog_json`/`models_updated_at`) | ✅ |
| `model_catalog` Pricing-Attribute | ✅ | ⚠️ `live_count`/`free_models`/`cheapest_model`/`cheapest_overall`/`ranking_by_cost` fehlen | ⚠️ CG-C1 (API: kein Pricing) |
| `live_models_count` | ✅ (Konto-Entry) | — | ⚠️ CG-C2 (API-blockiert) |
| `cheapest_model` | ✅ (Konto-Entry) | — | ⚠️ CG-C2 |
| `free_models` | ✅ (Konto-Entry) | — | ⚠️ CG-C2 |
| Credits (monthly/purchased/free/remaining) | — | ✅ (domain-erlaubt) | ✅ domain |
| Total cost / Requests / Tokens | — | ✅ (domain-erlaubt) | ✅ domain |
| `plan` | — | ✅ (domain-erlaubt) | ✅ domain |

## Binary Sensoren

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `rate_limited` (PROBLEM, je Fenster) | ✅ | ✅ | ✅ |
| `subscription_active` (kein device_class) | ✅ | ✅ | ✅ |
| `api_reachable` (konto-weit, tri-state auf Evidenz/TTL) | ✅ (accountweit: frischer Erfolg → ON, neutrale Antwort `no_subscription`/`auth_error` → unknown, nur frische Fehler → OFF, keine frische Evidenz → unknown; TTL 2× Konto-Intervall / 3× Usage-Intervall) | ✅ (`is_on` = `last_update_success` + `fetched_at`; bewusst immer `available`) | ✅ |
| `credits_below_threshold` | — | ✅ (domain-erlaubt) | ✅ domain CG-B4 |

## Settings

| Entity | go_gauge (Kanon) | command_gauge | Status |
|---|---|---|---|
| `warning_threshold` (% · 1–100 · `alert-octagon-outline`) | ✅ | ✅ | ✅ |
| `pace_red_limit` (% · `alert-decagram-outline`) | ✅ 1–300 | ⚠️ 1–1000 (domain: Forecast >300) | ⚠️ CG-N2 |
| `usage_refresh_min` (min · `timer-outline`) | ✅ 1–1440 | ⚠️ 5–1440 (Fair-Use) | ⚠️ CG-N3 |
| `models_refresh_min` (min · `timer-outline`) | ✅ 1–1440, Default 60 — **global auf der Konto-Entry** (`account_models_refresh_minutes`) | ⚠️ 60–1440 (Fair-Use), Entry-lokal | ⚠️ CG-N4 |
| `auto_update_usage` | ✅ (workspace-lokal, `recalculate_interval()`) | ✅ | ✅ |
| `auto_update_models` | ✅ **global auf der Konto-Entry** (`account_auto_update_models`, Default ON, `set_auto_fetch` + `persist_account_options`, kein Reload) | ✅ (Entry-lokal) | ✅ |
| `refresh` (workspace) | ✅ nur Usage-Zyklus | ✅ | ✅ |
| `refresh` (Konto) | ✅ `account_refresh`, nur Katalog-Fetch | ✅ (eigene Entry) | ✅ |
| `burn_lookback_5h` (min · 15–300 · slider · `mdi:history`) | ✅ aktiv (2.1.0), `entity_category: config`, Step 5 | ⚠️ CG-N5 | ⚠️ |
| `burn_lookback_week` (min · 60–10080 · slider · `mdi:history`) | ✅ aktiv (2.1.0), `entity_category: config`, Step 60 | ⚠️ CG-N5 | ⚠️ |
| `burn_lookback_month` (min · 60–10080 · slider · `mdi:history`) | ✅ aktiv (2.1.0), `entity_category: config`, Step 60 | ⚠️ CG-N5 | ⚠️ |
| `reset_burn_lookbacks` (button · `mdi:restore` · diagnostic) | ✅ aktiv (2.1.0), `unique_id` `burn_lookback_reset` | ⚠️ CG-B6 | ⚠️ |

**Aktiv in Kanon v1.7.0 (go_gauge 2.1.0):** Die drei Burn-Lookback-Numbers und der
Reset-Button sind jetzt **Core-Entities** (§8.4, `entities`-Liste statt
`domain_extensions`) und damit prüfpflichtig — inklusive `mode: slider`, `step`
(5/60/60), `default` (120/720/2880), `entity_category` (`config` bzw. `diagnostic`)
und `unique_id`-Suffixen (`burn_lookback_*_minutes`, `burn_lookback_reset`). Der
Checker prüft `mode`/`step`/`default`/`entity_category` statisch (D16). Ebenfalls
aktiv: das **echte Kalendermonat** aus `resetsAt` (§2) und die D22-Diagnose-Attribute
(`burn_rate`: `lookback_minutes`/`samples`/`lookback_too_short`; `forecast`/`pace`:
`forecast_recent`/`forecast_method`/`elapsed_fraction`/`window_seconds`).
command_gauge hat die vier Entities noch nicht (⚠️ CG-N5 / ⚠️ CG-B6) und liefert die
D22-Attribute ebenfalls noch nicht (⚠️ CG-C3, offener Paar-Change).

## Namen / Wortstellung

| Aspekt | go_gauge | command_gauge | Status |
|---|---|---|---|
| EN-Master, Fenster-Placeholder **vorn** (`{window} Usage`) | ✅ | ✅ | ✅ |
| `strings.json` + `translations/{en,de}.json` vollständig | ✅ | ✅ | ✅ |
| `Burn-Rate`-Schreibweise EN | ✅ | ✅ | ✅ |

## Entity-Kategorien (v1.8.0)

Reine UI-/Registry-Metadaten; **keine** Änderung an `unique_id`, `entity_id`,
State, Historie oder Automationen. Device-Topologie bleibt unverändert; keine
Trennung nach Stunden/Woche/Monat über Kategorien (nur über Namen/Keys).

| Entity-Gruppe | Kategorie | go_gauge | command_gauge | Status |
|---|---|---|---|---|
| Settings-Numbers (`warning_threshold`, `pace_red_limit`, `usage_refresh_min`, `models_refresh_min`) | `config` | ✅ ab 2.1.1 | ⚠️ Transition (Paar-Change) | — |
| Burn-Lookback-Numbers (`burn_lookback_5h/week/month`) | `config` | ✅ | ⚠️ CG-N5 (Entities fehlen) | ⚠️ |
| Auto-Update-Switches (`auto_update_usage`, `auto_update_models`) | `config` | ✅ ab 2.1.1 | ⚠️ Transition (Paar-Change) | — |
| Reset-Button (`reset_burn_lookbacks`) | `diagnostic` | ✅ | ⚠️ CG-B6 (Button fehlt) | ⚠️ |
| Primärdaten (Sensoren/Binary-Sensoren) | `null` | ✅ | ✅ | ✅ |
| Refresh-Buttons (`refresh`, `account_refresh`) | `null` | ✅ | ✅ | ✅ |

**Übergang:** Solange die Consumer noch `null` liefern, sind die neuen
`config`-Werte im Schema nicht erzwungen (Phase A). Nach dem Paar-Change
erzwingt Phase B die exakten Werte; es entstehen **keine neuen CG-IDs**.

## Repository-Hygiene (v1.7.0)

Gilt **zusätzlich** zum Entity-Kanon (`canon/repository.md`); keine Entity-,
`unique_id`- oder Übersetzungsänderung. Custom Repository über den My-Link ist
der primäre Weg, der Katalog-Eintrag bleibt optional.

| Aspekt | go_gauge 2.0.2 | command_gauge | Status |
|---|---|---|---|
| README-Paar EN/DE, identischer Language Switcher in Zeile 1 | ✅ | ⚠️ nur `README.md` | — |
| My-Link (`hacs_repository` + Badge) | ✅ | ⚠️ fehlt | — |
| Screenshot unter `docs/images/`, aus README referenziert | ✅ | ⚠️ fehlt | — |
| `hacs.json` (`name`, `homeassistant`, **kein** `render_readme`; `zip_release`/`hide_default_branch` nur mit Begründung) | ✅ | ⚠️ `render_readme` + `zip_release` vorhanden | — |
| `manifest.json` (domain/name/version/documentation/issue_tracker/codeowners/config_flow/integration_type/iot_class) | ✅ | ✅ | — |
| `brand/icon.png` (PNG, 256×256) | ✅ | ✅ | — |
| Tag ↔ `manifest.version` synchron | ✅ `v2.0.2` ↔ `2.0.2` | ⚠️ Tag `v1.2.0` ↔ `2.0.0` | — |
| Community-Dateien (Issue-/PR-Templates, CONTRIBUTING, SECURITY, CoC, CODEOWNERS, Dependabot) | ✅ | ⚠️ fehlen | — |
| CI: HACS Action + hassfest + `pytest`/`ruff`/`mypy`/`check_json_consistency`/`check_canon` (Pflicht), `schedule` + `workflow_dispatch` (empfohlen), kein `ignore:` | ✅ | ⚠️ `schedule` fehlt | — |
| Releases: SemVer, volles GitHub-Release, `CHANGELOG.md`-Block | ✅ | ⚠️ CHANGELOG-Block vorhanden, Tag-Sync offen | — |
| Hygiene-Checker (`check_repo_hygiene.py`) | ✅ 0 Fehler / 0 Warnungen | ⚠️ offen (`--warn-only`, Exit 0) | — |
| Entity-ID-/Namensregel dokumentiert | ✅ | ⚠️ offen (Transition) | — |

**command_gauge: ⚠️ Transition (offen)** — kein Entity-Bruch und **kein
CG-Eintrag**. Schließungsbedingung: „Hygiene-Contract umgesetzt (README EN/DE,
Templates, Community-Dateien, Checker grün)“. Bis dahin läuft der Checker mit
`--warn-only`.

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
   `pace_red_percent`, `usage_minutes`) sind bewusst identisch und bleiben es.
   Seit go_gauge 2.0.0 liegen die Modell-Settings auf der Konto-Entry
   (`AccountCoordinator.auto_fetch` / `base_interval_minutes` /
   `persist_account_options`) statt auf der Workspace-Entry (`auto_models` /
   `models_minutes`) — der Konto-Split ist go_gauge-spezifisch (§13.3).
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
| CG-D1 | kein Account-Device / keine Konto-ConfigEntry | entfällt (kein Duplikat-Problem; go_gauge nutzt eine eigene Konto-Entry) |
| CG-N2 | `pace_red_limit` Range 1–1000 | domain-begründet, entfällt |
| CG-N3 | `usage_refresh_min` Min 5 | domain-begründet (Fair-Use), entfällt |
| CG-N4 | `models_refresh_min` Min 60 | domain-begründet (Fair-Use), entfällt |
| CG-N5 | Burn-Lookback-Numbers fehlen (`burn_lookback_5h`/`week`/`month`) | command_gauge liefert die drei Number-Entities |
| CG-B6 | Reset-Button `reset_burn_lookbacks` fehlt | command_gauge liefert den Reset-Button |
| CG-C3 | D22-Attribute an `forecast`/`pace` (`forecast_recent`/`forecast_method`/`elapsed_fraction`/`window_seconds`) und `burn_rate` (`lookback_minutes`/`samples`/`lookback_too_short`) fehlen | command_gauge liefert die Diagnose-Attribute |

**In v1.7.0 (go_gauge 2.1.0):** Burn-Lookback aktiviert — die drei
Number-Slider (`entity_category: config`, Steps 5/60/60, Defaults 120/720/2880)
und der Reset-Button (`entity_category: diagnostic`, `unique_id`
`burn_lookback_reset`) sind Core-Entities (§8.4). Zusätzlich verbindlich: die
Burn-Rate als **OLS-Steigung** über das Lookback-Fenster, die D22-Diagnose-Attribute
(`burn_rate`, `forecast`, `pace`) und das **echte Kalendermonat** aus `resetsAt`
(§2). Der Checker prüft `mode`/`step`/`default`/`entity_category` statisch (D16).
command_gauge: ⚠️ **CG-N5** (drei Numbers), ⚠️ **CG-B6** (Reset-Button) und
⚠️ **CG-C3** (D22-Attribute) registriert — der Paar-Change steht dort noch aus,
der Checker bleibt damit bei **0 Fehlern**.

**In v1.6.0 (go_gauge 2.0.0):** Konto-Vertrag auf die eigene Konto-ConfigEntry
gehoben (Kanon §13) — 8 Konto-Entities mit `account_`-Präfix, `api_reachable`
accountweit auf Evidenz/TTL (Tri-State), Refresh-Split (Workspace = nur
Usage-Zyklus, Konto = nur Katalog-Fetch), Modell-Settings global auf der
Konto-Entry (Default ON / 60, Range 1–1440), HA-Minimum 2026.8.0, Migration
v7→v8 mit erhaltener `entity_id`/History. Die frühere
„Catalog Owner / erste Workspace-Instanz"-Regel entfällt ersatzlos; CG-D1
bleibt als Doku-Info, **kein neuer ⚠️-Eintrag**. command_gauge unberührt
(1 Entry = 1 Konto).

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
