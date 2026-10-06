# Gauge Entity Canon v1.2

Verbindliche Spezifikation des Entity-Modells aller Gauge-Integrationen
(`go_gauge`, `command_gauge`). Master/Stil-Referenz: **ha-go-gauge 1.6.0**.
Abweichungen sind nur als registrierter ⚠️-Eintrag erlaubt
(→ Abschnitt „Ausnahmeregelung").

> **Seit Kanon v1.2 (2026-10-06):** `command_gauge` **1.0.0** hat die Konvergenz
> vollzogen — `translation_keys`, `{window}`-Wortstellung, Icons, `usage`-Status/
> Attribute, `model_catalog`, `subscription_active` (ohne `device_class`) und die
> Settings-Keys sind kanonisch; die Legacy-Alias-Keys sind entfallen und die
> Legacy-`unique_id`-Suffixe wurden per Entity-Registry-Migration auf die
> Kanon-Suffixe umgeschrieben (Historie bleibt erhalten). Registriert sind nur
> noch **API-blockierte** (month-Fenster, `api_status`, Pricing-Katalog) und
> **domain-begründete** (Number-Ranges) Abweichungen.

Maschinenlesbare Version: `canon/entities.schema.json`
(diese Datei ist die normative Referenz bei Widersprüchen).

## 1. Device-Topologie

| Aspekt | Kanon |
|---|---|
| Device pro Config-Entry, identifiziert via `identifiers: {(DOMAIN, entry.entry_id)}` | verbindlich |
| Device-Name | `f"{Brand} {Scope}"` — go_gauge: `Go Gauge {workspace_name}`; command_gauge: `Command Gauge {account_name}` |
| `manufacturer` | `Popoboxxo` (beide Integrationen) |
| `model` | API-Produktname — go_gauge: `OpenCode Go`; command_gauge: `CommandCode Cloud` |
| Account-Device (konto-/workspace-übergreifende Entities) | go_gauge: separates Device `Go Gauge Konto` mit `identifiers: {(DOMAIN, "account")}`, Katalog-Entities nur vom *Catalog Owner* (erste Instanz). command_gauge: entfällt (jeder Entry = eigenes Konto, kein Duplikat-Problem) ⚠️ CG-D1 |
| `_attr_has_entity_name = True` global; kein `_attr_name`-Literal irgendwo | verbindlich (HACS-eiserne Regel) |

## 2. Fenster (Windows)

| Fenster | Label (EN, `WINDOW_LABELS`) | Nominaldauer (`WINDOW_SECONDS`) |
|---|---|---|
| `5h` | `5h rolling` | 18 000 s |
| `week` | `Weekly` | 604 800 s |
| `month` | `Monthly` | 2 592 000 s (30-Tage-Näherung) ⚠️ CG-W1 |

Fenster-Labels werden als `{window}`-Placeholder in `translation_placeholders`
gesetzt; die Fenster-Entities werden dynamisch aus der Fenster-Liste erzeugt
(deshalb skaliert der 7er-Satz automatisch auf neue Fenster).

## 3. Fenster-Sensor-Satz (7er-Satz, je Fenster)

Pro Fenster existieren exakt diese 7 Sensoren. `unique_id`-Schema:
`f"{entry.entry_id}_{scope}_{window}_{suffix}"` (scope = workspace_key /
account scope). Reihenfolge der Suffixe ist Kanon.

| # | Konzept | translation_key | Unit | device_class | state_class | Icon(s) | unique_id-Suffix | EN-Name |
|---|---|---|---|---|---|---|---|---|
| 1 | Usage | `usage` | `%` | — | MEASUREMENT | `mdi:speedometer` (dyn.: `mdi:shield-off-outline` bei `no_subscription`) | `percent` | `{window} Usage` |
| 2 | Reset | `reset` | — | TIMESTAMP | — | `mdi:timer-reset` | `reset` | `{window} Reset` |
| 3 | Forecast | `forecast` | `%` | — | MEASUREMENT | `mdi:trending-up` | `forecast` | `{window} Forecast` |
| 4 | Pace | `pace` | — | — | — | dyn. nach Status: green `mdi:check-circle-outline`, yellow `mdi:alert-circle-outline`, red `mdi:close-circle-outline`, default `mdi:speedometer-medium` | `pace` | `{window} Pace` |
| 5 | Remaining | `remaining` | `%` | — | MEASUREMENT | `mdi:gauge` | `remaining` | `{window} Remaining` |
| 6 | Time to Reset | `time_to_reset` | `h` | DURATION | — | `mdi:timer-sand` | `time_to_reset` | `{window} Time to Reset` |
| 7 | Burn Rate | `burn_rate` | `%/h` | — | MEASUREMENT | `mdi:fire` | `burn_rate` | `{window} Burn-Rate` |

**Verhalten (Kanon, go_gauge):**

- **Usage:** State `None` bei `no_subscription`/`error` (kein String-State auf
  MEASUREMENT-% — HA 2026.9 lehnt das hart ab). Status bleibt über Icon +
  Attribute + Binary-Sensoren sichtbar.
- **Forecast:** lineare Projektion `percent / elapsed_fraction`, darf > 100 %
  zeigen; `None` direkt nach Reset (keine Fake-Zahl).
- **Pace:** State `green`/`yellow`/`red` nach Forecast vs. zwei Number-Grenzen;
  Attribute: `forecast_percent`, `green_below`, `red_above`.
- **Remaining:** `100 − genutzt %`; `None` (nie 100) bei fehlendem Abo/Fehler.
- **Time to Reset:** Sekunden/3600 als `h`; **Burn Rate:** Steigung der letzten
  2 h in `%/h`.
- **Attribute Usage:** `workspace_key`, `window`, `status`, `note`,
  `resets_at_iso`.

✅ **CG-W2/CG-W3 (command_gauge, geschlossen in 1.0.0):** Keys sind kanonisch
(`usage`, `reset`, `forecast`, `pace`, `remaining`, `time_to_reset`,
`burn_rate`); der `usage`-Sensor liefert `None` bei `no_subscription`/`error`
(Icon `mdi:shield-off-outline`) und trägt `workspace_key`, `window`, `status`,
`note`, `resets_at_iso`; unique_id-Suffix `percent` (per Registry-Migration,
Historie erhalten).

## 4. Scope-Status: API Status (Sensor, je Scope)

Ursachen-Sensor der Erreichbarkeits-Familie (neu in go_gauge 1.6.0): benennt,
**warum** ein Scope (keine) Daten liefert — Ergänzung zum Ja/Nein der
Binary-Sensoren. Anlass: Der Abo-Sensor renderte mit CONNECTIVITY „Getrennt"
und wurde als API-Ausfall fehlinterpretiert.

| Konzept | translation_key | device_class | States | Icon | unique_id-Suffix | Attribute | EN-Name |
|---|---|---|---|---|---|---|---|
| API Status (je Scope) | `api_status` | ENUM | `ok`, `no_subscription`, `rate_limited`, `auth_error`, `api_error`, `unknown` | `mdi:cloud-alert` | `api_status` | `workspace_key`, `raw_status`, `note`, `last_update_success` | `API Status` |

**Verhalten (Kanon, go_gauge):**

- Bewusst **je Scope**, nicht accountweit: der accountweite `api_reachable`
  aggregiert („irgendwas ging schief") und verdeckt genau den Mix aus
  liefert-Daten/kein-Abo zwischen Scopes.
- Auflösung: `ok` = API liefert Nutzungsdaten; `ok` + ein rate-limitedes
  Fenster → `rate_limited` (relevantere Ursache als „alles gut" bei 100 %);
  `no_subscription` = 403 EntitlementError (Token gültig, Abo fehlt);
  `error` mit `AuthError`/`401` in `note` → `auth_error` (Konfig-Problem,
  kein Code-Bug); sonstiger `error` (403 ohne Entitlement, 5xx, Netz) →
  `api_error` (transient); Workspace unbekannt oder Status fremd → `unknown`.
- Enum-States werden **roh** gerendert (keine lokalisierten
  `state`-Übersetzungen) — Marken/Alarme bauen auf den stabilen Keys.
- Keine Unit, kein state_class; `entity_registry_enabled_default = True`.

⚠️ **CG-B5:** command_gauge implementiert `api_status` nicht — die
CommandCode-API liefert den Abo-/API-Status nur konto-weit
(`subscription.status`: active/trialing/paid/…), kein Scope-Status-Modell
mit `no_subscription`/`rate_limited`. — *Schließung:* nur bei API-Erweiterung
(vgl. CG-W3, CG-C2).

## 5. Binary Sensoren

| Konzept | translation_key | device_class | Icon | unique_id-Suffix | Attribute | EN-Name |
|---|---|---|---|---|---|---|
| Rate Limited (je Fenster) | `rate_limited` | PROBLEM | `mdi:block-helper` | `limited` | — | `{window} rate-limited` |
| Subscription Active (je Scope) | `subscription_active` | — (keine) | `mdi:shield-check-outline` | `subscription_active` | `workspace_key`, `note` | `Subscription Active` |
| API Reachable (konto-weit) | `api_reachable` | CONNECTIVITY | — (HA-Default) | `api_reachable` | — | `API Reachable` |

Verhalten: `rate_limited` ON bei Fenster-Status `rate-limited`; bei
`no_subscription`/Update-Fehler `unavailable` (nicht OFF).
`api_reachable` ON bei `last_update_success` und vorhandenem `fetched_at`;
nur vom Catalog Owner (go_gauge).
`subscription_active` ON bei Scope-Status `ok`, OFF bei `no_subscription`
(Attribut `note` trägt die Ursache), sonst `unknown` (None). **Kein
device_class** (Kanon seit 1.6.0): CONNECTIVITY ließ HA den Zustand als
„Getrennt" rendern — ein Abo ist ein Subskriptionszustand, keine Verbindung;
Verbindung ist allein Sache von `api_reachable`.

✅ **CG-B1/B2/B3 (command_gauge, geschlossen in 1.0.0):** `rate_limited` ist
kanonisch (Icon `mdi:block-helper`, Suffix `limited`, `unavailable` statt OFF
ohne Abo); `api_reachable` ist kanonisch benannt (`is_on` = `last_update_success`
+ `fetched_at`, bewusst weiterhin immer `available` — Konto-Sensor); der
`subscription_active`-Sensor hat **keinen** `device_class` mehr und trägt
`mdi:shield-check-outline` plus `workspace_key`/`note`.
⚠️ **CG-B4 (domain-spezifisch, erlaubt):** `credits_below_threshold`
(PROBLEM, ON wenn Guthaben unter API-Schwelle) — command_code Credit-Modell,
kein go_gauge-Äquivalent. *Schließung:* entfällt.

## 6. Katalog-Sensoren (Modell-Katalog)

Grundsatz: **EIN Sensor trägt den kompletten Katalog als dynamische
JSON-Attribute** — neue Modelle erscheinen ohne neue Entities.

| Konzept | translation_key | state_class | Icon | unique_id-Suffix | EN-Name |
|---|---|---|---|---|---|
| Model Catalog | `model_catalog` | MEASUREMENT | `mdi:format-list-bulleted` | `model_catalog` | `Models` |
| Live Models Count | `live_models_count` | MEASUREMENT | `mdi:check-network-outline` | `models_live_count` | `Live Models` |
| Cheapest Model | `cheapest_model` | — | `mdi:crown-outline` | `cheapest_model` | `Cheapest Model` |
| Free Models | `free_models` | — | `mdi:gift-outline` | `free_models` | `Free Models` |

Attribute `model_catalog` (Kanon): `models_updated_at`, `count`,
`live_count`, `free_models`, `cheapest_model`, `cheapest_overall`,
`ranking_by_cost` (nach Kosten-Nutzen-Ratio, nur live), `catalog_json`
(kompletter Katalog als JSON-String).
Attribute `cheapest_model`: `cheapest_overall`, `ratio_usd_per_1m`.

⚠️ **CG-C1:** command_gauge `model_catalog` ist kanonisch benannt und trägt
`count`, `catalog_json`, `models_updated_at`; die Pricing-Attribute
(`live_count`, `free_models`, `cheapest_model`, `cheapest_overall`,
`ranking_by_cost`) fehlen, weil CommandCode nur id/name/context_length liefert.
— *Schließung:* CommandCode `/provider/v1/models` liefert Pricing →
`build_models_block` erweitern, Kanon-Attribute spiegeln.
⚠️ **CG-C2 (API-blockiert):** `live_models_count`, `cheapest_model`,
`free_models` existieren in command_gauge nicht — die CommandCode-API
liefert keine Pricing-Daten. — *Schließung:* nur bei API-Erweiterung
(siehe CG-C1).

## 7. Credit-/Summary-Sensoren (⚠️ domain-spezifisch, command_code-only)

Das Credit-/Billing-Modell ist command_code-spezifisch und **erlaubte
Domain-Erweiterung** — go_gauge hat kein Credit-Modell. Einheit:
`USD`, state_class MEASUREMENT (Zähler ohne sinnvolle device_class).

| translation_key | Unit | Icon | unique_id | EN-Name |
|---|---|---|---|---|
| `monthly_credits` | USD | `mdi:calendar-month` | `{entry_id}_monthly_credits` | `Monthly credits` |
| `purchased_credits` | USD | `mdi:shopping` | `{entry_id}_purchased_credits` | `Purchased credits` |
| `free_credits` | USD | `mdi:gift-outline` | `{entry_id}_free_credits` | `Free credits` |
| `remaining_credits` | USD | `mdi:wallet` | `{entry_id}_remaining_credits` | `Remaining credits` |
| `total_cost` | USD | `mdi:cash` | `{entry_id}_total_cost` | `Total cost` |
| `request_count` | — | `mdi:counter` | `{entry_id}_total_count` | `Requests` |
| `token_count` | — | `mdi:counter` | `{entry_id}_total_tokens` | `Tokens` |
| `plan` | — | `mdi:shield-account-outline` | `{entry_id}_plan` | `Plan` |

*Schließung:* entfällt (API-Modell-Differenz, dokumentiert statt
nachgebildet).

## 8. Settings-Entities

### 8.1 Numbers (4) — Wertebereiche sind Kanon (go_gauge-Werte)

Alle: `NumberMode.BOX`, `native_step = 1`, Unit wie angegeben, sofort
wirksam + persistent via `persist_options` (ohne Entry-Reload).

| # | translation_key | Unit | Min | Max | Default | Icon | unique_id-Suffix | EN-Name |
|---|---|---|---|---|---|---|---|---|
| 1 | `warning_threshold` | `%` | **1** | **100** | 80 | `mdi:alert-octagon-outline` | `warn_percent` | `Warning Threshold` |
| 2 | `pace_red_limit` | `%` | **1** | **300** | 100 | `mdi:alert-decagram-outline` | `pace_red_percent` | `Pace Red Limit` |
| 3 | `usage_refresh_min` | `min` | **1** | **1440** | 10 | `mdi:timer-outline` | `usage_refresh_minutes` | `Usage Refresh (min)` |
| 4 | `models_refresh_min` | `min` | **1** | **1440** | 60 | `mdi:timer-outline` | `models_refresh_minutes` | `Models Refresh (min)` |

Die Schwellen gelten einheitlich für ALLE Fenster (nicht je Fenster).
Defaults zusätzlich als Konstanten: `DEFAULT_WARN_PERCENT=80`,
`DEFAULT_PACE_RED_PERCENT=100`, `DEFAULT_USAGE_REFRESH_MINUTES=10`,
`DEFAULT_MODELS_REFRESH_MINUTES=60`.

✅ **CG-N1 (Keys/Icons geschlossen in 1.0.0):** command_gauge nutzt jetzt die
Kanon-Keys `warning_threshold`, `pace_red_limit`, `usage_refresh_min`,
`models_refresh_min` mit den Kanon-Icons (`mdi:alert-octagon-outline`,
`mdi:alert-decagram-outline`, `mdi:timer-outline`). ⚠️ **domain-begründete
Ranges bleiben:** `pace_red_limit` 1–**1000** (Forecast darf >300 projizieren),
`usage_refresh_min` Min **5** und `models_refresh_min` Min **60**
(CommandCode-API-Fair-Use). *Schließung:* entfällt (domain-begründet).

### 8.2 Switches (2)

| translation_key | Icon | unique_id-Suffix | EN-Name |
|---|---|---|---|
| `auto_update_usage` | `mdi:autorenew` | `auto_update_usage` | `Auto Update Usage` |
| `auto_update_models` | `mdi:autorenew` | `auto_update_models` | `Auto Update Models` |

Beide schalten den jeweiligen Auto-Refresh-Zyklus und triggern
`recalculate_interval()`; persistiert via `persist_options`.

✅ **CG-S1 (geschlossen in 1.0.0):** command_gauge nutzt `auto_update_usage` /
`auto_update_models` (Icons identisch, unique_id-Suffix kanonisch).

### 8.3 Button (1)

| translation_key | Icon | unique_id-Suffix | EN-Name |
|---|---|---|---|
| `refresh` | `mdi:refresh` | `refresh` | `Refresh` |

Erzwingt sofortigen Refresh **beider** Zyklen (usage + models), unabhängig
von den Auto-Update-Schaltern. ✅ beide Integrationen identisch.

## 9. Namensschema / Wortstellung

- **Kanon-Wortstellung (go_gauge-Stil):** Fenster-Placeholder **vorn**:
  `{window} Usage`, `{window} Reset`, `{window} Forecast`, `{window} Pace`,
  `{window} Remaining`, `{window} Time to Reset`, `{window} Burn-Rate`,
  `{window} rate-limited`.
- **Master-Sprache Englisch** in `strings.json` (= Identität);
  `translations/de.json` lokalisiert den Anzeigenamen (`{window} Nutzung`,
  …). `entity_id`/object_id bleibt sprachstabil (siehe Object-ID-Pinning,
  offener Punkt OP-1).
- `Burn-Rate` wird im EN-Master als `Burn-Rate` (Binnenmajuskel-Wort)
  geschrieben — Kanon gegenüber `Burn rate`.
- Kein hartcodiertes `_attr_name`/`name`-Literal; Anzeigename ausschließlich
  über `_attr_translation_key` (eiserne Regel).

✅ **CG-NAME1 (geschlossen in 1.0.0):** command_gauge stellt das Fenster jetzt
vorn (`{window} Usage`, `{window} Burn-Rate`, `{window} rate-limited`, …).

## 10. Ausnahmeregelung (⚠️-Regime)

1. Domain-begründete Divergenz ist nur gültig mit ⚠️-Eintrag **in diesem
   Kanon** (Begründung + Schließungsbedingung) — nicht durch stille
   Nachbildung, nicht durch „lokal dokumentiert".
2. Jeder ⚠️-Eintrag trägt eine ID (`CG-xx`), die in der Feature-Matrix
   (`matrix/parity.md`) gespiegelt wird.
3. Bei jedem Release beider Repos wird jeder ⚠️-Eintrag auf
   „inzwischen umsetzbar?" geprüft (API-Änderungen).
4. Neue, nicht registrierte Abweichungen sind **Fehler** — der Checker
   (`scripts/check_canon.py`) meldet sie als ERROR (Exit 1), registrierte
   als WARNING (⚠️, Exit 0).

## 11. Offene Kanon-Punkte (gelten für beide Integrationen)

| ID | Punkt | Stand |
|---|---|---|
| OP-1 | `suggested_object_id`-Pinning auf Englisch (Vorbild `ha-health-o-mat`) — beide Repos ohne Pinning; command_gauge hat deutsch Erstregistrierte Slugs (0.1.1) | Koordinierte Umsetzung + Registry-Migration geplant |
