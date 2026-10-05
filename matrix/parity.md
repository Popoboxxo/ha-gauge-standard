# Gauge Parity-Matrix (Pflegedatei)

Stand: 2026-10-05 · Kanon **v1.1** (`canon/entities.md`, Master = go_gauge 1.6.0) ·
Vorgänger: `docs/parity-with-go-gauge.md` in ha-command-gauge (wird von dieser
Datei abgelöst, sobald die Submodule-Einbindung steht).

**Legende:** ✅ = Kanon erfüllt · ⚠️ = registrierte Abweichung (mit Kanon-ID und
Schließungsbedingung) · ❌ = unregistrierte Abweichung = Fehler · — = existiert
nicht (domain-seitig begründet).

Checker-Ergebnisse (Stand 2026-10-05):
`check_canon.py` → go_gauge: **0 Fehler / 0 Warnungen** (Referenz = grün) ·
command_gauge: **0 Fehler / 54 registrierte Warnungen** (Exit 0).

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
| `usage` (% · MEASUREMENT · suffix `percent`) | ✅ | ⚠️ `window_usage`, Suffix `usage`, keine Status-Attribute | ⚠️ CG-W2/W3 |
| `reset` (TIMESTAMP) | ✅ | ✅ (Alias `window_reset`) | ⚠️ CG-W2 (nur Key) |
| `forecast` (%, MEASUREMENT) | ✅ | ✅ (Alias `window_forecast`) | ⚠️ CG-W2 |
| `pace` (Ampel + Attribute) | ✅ | ✅ vollständig (Alias `window_pace`) | ⚠️ CG-W2 |
| `remaining` (%) | ✅ | ✅ (Alias `window_remaining`) | ⚠️ CG-W2 |
| `time_to_reset` (DURATION, h) | ✅ | ✅ (Alias `window_time_to_reset`) | ⚠️ CG-W2 |
| `burn_rate` (%/h) | ✅ | ✅ (Alias `window_burn_rate`) | ⚠️ CG-W2 |
| Fenster | ✅ 5h/week/month | ⚠️ 5h/week | ⚠️ CG-W1 (API) |

## Scope-Status (je Scope)

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `api_status` (ENUM-Ursache statt Ja/Nein) | ✅ (seit 1.6.0) | — (API: kein Scope-Status-Modell) | ⚠️ CG-B5 (API-blockiert) |

## Konto- / Katalog-Sensoren

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `model_catalog` (Kanon-Attribute voll) | ✅ | ⚠️ `models`, nur `catalog_json`/`models_updated_at` | ⚠️ CG-C1 (API: kein Pricing) |
| `live_models_count` | ✅ | — | ⚠️ CG-C2 (API-blockiert) |
| `cheapest_model` | ✅ | — | ⚠️ CG-C2 |
| `free_models` | ✅ | — | ⚠️ CG-C2 |
| Credits (monthly/purchased/free/remaining) | — | ✅ (domain-erlaubt) | ✅ domain |
| Total cost / Requests / Tokens | — | ✅ (domain-erlaubt) | ✅ domain |
| `plan` | — | ✅ (domain-erlaubt) | ✅ domain |

## Binary Sensoren

| Entity | go_gauge | command_gauge | Status |
|---|---|---|---|
| `rate_limited` (PROBLEM, je Fenster) | ✅ | ⚠️ `window_exceeded`, kein Icon, Suffix `exceeded` | ⚠️ CG-B1 |
| `subscription_active` (kein device_class) | ✅ | ⚠️ RUNNING, keine Attribute, kein Icon | ⚠️ CG-B3 |
| `api_reachable` (konto-weit) | ✅ (Catalog Owner) | ⚠️ `account_reachable`, immer verfügbar | ⚠️ CG-B2 |
| `credits_below_threshold` | — | ✅ (domain-erlaubt) | ✅ domain CG-B4 |

## Settings

| Entity | go_gauge (Kanon) | command_gauge | Status |
|---|---|---|---|
| `warning_threshold` (% · 1–100 · `alert-octagon-outline`) | ✅ | ⚠️ `warn_percent`, Icon `mdi:alert` | ⚠️ CG-N1 |
| `pace_red_limit` (% · **1–300** · `alert-decagram-outline`) | ✅ | ⚠️ `pace_red_percent`, **1–1000**, Icon abweichend | ⚠️ CG-N1 |
| `usage_refresh_min` (min · **1–1440** · `timer-outline`) | ✅ | ⚠️ `usage_refresh_minutes`, **5–1440**, Icon abweichend | ⚠️ CG-N1 |
| `models_refresh_min` (min · **1–1440** · `timer-outline`) | ✅ | ⚠️ `models_refresh_minutes`, **60–1440**, Icon abweichend | ⚠️ CG-N1 |
| `auto_update_usage` / `auto_update_models` | ✅ | ⚠️ `auto_usage` / `auto_models` (Icons ✅) | ⚠️ CG-S1 |
| `refresh` (erzwingt beide Zyklen) | ✅ | ✅ | ✅ |

## Namen / Wortstellung

| Aspekt | go_gauge | command_gauge | Status |
|---|---|---|---|
| EN-Master, Fenster-Placeholder **vorn** (`{window} Usage`) | ✅ | ⚠️ `Usage {window}` (hinten) | ⚠️ CG-NAME1 |
| `strings.json` + `translations/{en,de}.json` vollständig | ✅ | ✅ | ✅ |
| `Burn-Rate`-Schreibweise EN | ✅ | ⚠️ `Burn rate` | ⚠️ CG-NAME1 |

## Verfahren (unverändert aus dem Paritäts-Konzept übernomommen)

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
5. **Entity-Breaking = MAJOR** in dem Repo, in dem es passiert; `unique_id`
   nie ändern (Renames per Entity-Registry-Migration).
6. **Checker-Pflicht:** `scripts/check_canon.py` muss vor jedem Release gegen
   beide Repos grün laufen (Master: 0/0; Konvergenz-Ziel: 0 Fehler, nur
   registrierte ⚠️).

## Abweichungs-Index (⚠️-IDs)

| ID | Thema | Schließungsbedingung (Kurz) |
|---|---|---|
| CG-W1 | month-Fenster fehlt | CommandCode-API ergänzt Monatsfenster |
| CG-W2 | `window_*`-/`warn_percent`-Keys | Rename auf Kanon-Keys, MAJOR + Registry-Migration |
| CG-W3 | usage: kein no_subscription-Schutz | Abo-Status-Handling angleichen |
| CG-NAME1 | Wortstellung `Usage {window}` | mit CG-W2 |
| CG-B1 | `window_exceeded` statt `rate_limited` | mit CG-W2 |
| CG-B2 | `account_reachable` | Entscheidung mit CG-W2 |
| CG-B3 | subscription_active: RUNNING, keine Attribute | mit CG-W2 (Kanon: kein device_class) |
| CG-B4 | `credits_below_threshold` | domain-erlaubt, entfällt |
| CG-B5 | `api_status` fehlt | nur bei CommandCode-API-Erweiterung |
| CG-C1 | Katalog-Attribute unvollständig | CommandCode-API liefert Pricing |
| CG-C2 | live/cheapest/free-Modelle fehlen | nur bei API-Erweiterung |
| CG-N1 | Number-Keys/Icons/Ranges | Angleichung mit CG-W2 prüfen |
| CG-S1 | Switch-Keys `auto_*` | mit CG-W2 |
| CG-D1 | kein Account-Device/Catalog-Owner | entfällt (kein Duplikat-Problem) |

## Offene Punkte (beide Repos)

| ID | Punkt |
|---|---|
| OP-1 | `suggested_object_id`-Pinning auf Englisch (Vorbild `ha-health-o-mat`) — koordinierte Umsetzung + Registry-Migration geplant |
