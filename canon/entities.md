# Gauge Entity Canon v1

Verbindliche Spezifikation des Entity-Modells aller Gauge-Integrationen
(`go_gauge`, `command_gauge`). Master/Stil-Referenz: **ha-go-gauge 1.5.2**.
Abweichungen sind nur als registrierter ⚠️-Eintrag erlaubt
(→ Abschnitt „Ausnahmeregelung").

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

⚠️ **CG-W2 (command_gauge, translation_keys):** `window_usage`,
`window_reset`, `window_forecast`, `window_pace`, `window_remaining`,
`window_time_to_reset`, `window_burn_rate`. — *Schließung:* Umbenennung auf
die Kanon-Keys im nächsten breaking Release (MAJOR).
⚠️ **CG-W3 (command_gauge, usage):** kein `no_subscription`-Schutz, keine
Attribute, unique_id-Suffix `usage` statt `percent`. — *Schließung:* dto.

## 4. Binary Sensoren

| Konzept | translation_key | device_class | Icon | unique_id-Suffix | Attribute | EN-Name |
|---|---|---|---|---|---|---|
| Rate Limited (je Fenster) | `rate_limited` | PROBLEM | `mdi:block-helper` | `limited` | — | `{window} rate-limited` |
| Subscription Active (je Scope) | `subscription_active` | CONNECTIVITY | `mdi:shield-check-outline` | `subscription_active` | `workspace_key`, `note` | `Subscription Active` |
| API Reachable (konto-weit) | `api_reachable` | CONNECTIVITY | — (HA-Default) | `api_reachable` | — | `API Reachable` |

Verhalten: `rate_limited` ON bei Fenster-Status `rate-limited`; bei
`no_subscription`/Update-Fehler `unavailable` (nicht OFF).
`api_reachable` ON bei `last_update_success` und vorhandenem `fetched_at`;
nur vom Catalog Owner (go_gauge).

⚠️ **CG-B1:** command_gauge nutzt `window_exceeded` (Alias, kein Icon,
Suffix `exceeded`) — Semantik „Fenster-Limit überschritten" entspricht
`rate_limited`. — *Schließung:* Umbenennung mit CG-W2.
⚠️ **CG-B2:** `account_reachable` (Alias zu `api_reachable`, immer
`available`, auch bei API-Ausfall — Absicht). — *Schließung:* kein Rename
nötig, aber Kanon-Attribut-Verhalten angleichen; Entscheidung mit CG-W2.
⚠️ **CG-B3:** command_gauge `subscription_active` mit device_class RUNNING
statt CONNECTIVITY. — *Schließung:* dto. (MAJOR).
⚠️ **CG-B4 (domain-spezifisch, erlaubt):** `credits_below_threshold`
(PROBLEM, ON wenn Guthaben unter API-Schwelle) — command_code Credit-Modell,
kein go_gauge-Äquivalent. *Schließung:* entfällt.

## 5. Katalog-Sensoren (Modell-Katalog)

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

⚠️ **CG-C1:** command_gauge: `models` (Alias zu `model_catalog`) mit nur
`catalog_json`, `models_updated_at`. — *Schließung:* CommandCode
`/provider/v1/models` liefert Pricing → `build_models_block` erweitern,
Kanon-Attribute spiegeln.
⚠️ **CG-C2 (API-blockiert):** `live_models_count`, `cheapest_model`,
`free_models` existieren in command_gauge nicht — die CommandCode-API
liefert keine Pricing-Daten. — *Schließung:* nur bei API-Erweiterung
(siehe CG-C1).

## 6. Credit-/Summary-Sensoren (⚠️ domain-spezifisch, command_code-only)

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

## 7. Settings-Entities

### 7.1 Numbers (4) — Wertebereiche sind Kanon (go_gauge-Werte)

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

⚠️ **CG-N1 (domain-begründet):** command_gauge nutzt
`usage_refresh_minutes` (Min **5**), `models_refresh_minutes` (Min **60**),
`warn_percent`, `pace_red_percent` (Max **1000**), Icons
`mdi:timer-refresh(-outline)`, `mdi:alert`, `mdi:alert-circle-outline`.
Min/Max bewusst enger (CommandCode-API-Limiten/Fair-Use), translation_keys
mit CG-W2-Schlüsselung umbenennen.

### 7.2 Switches (2)

| translation_key | Icon | unique_id-Suffix | EN-Name |
|---|---|---|---|
| `auto_update_usage` | `mdi:autorenew` | `auto_update_usage` | `Auto Update Usage` |
| `auto_update_models` | `mdi:autorenew` | `auto_update_models` | `Auto Update Models` |

Beide schalten den jeweiligen Auto-Refresh-Zyklus und triggern
`recalculate_interval()`; persistiert via `persist_options`.

⚠️ **CG-S1:** command_gauge: `auto_usage` / `auto_models` (Icon identisch).
— *Schließung:* mit CG-W2.

### 7.3 Button (1)

| translation_key | Icon | unique_id-Suffix | EN-Name |
|---|---|---|---|
| `refresh` | `mdi:refresh` | `refresh` | `Refresh` |

Erzwingt sofortigen Refresh **beider** Zyklen (usage + models), unabhängig
von den Auto-Update-Schaltern. ✅ beide Integrationen identisch.

## 8. Namensschema / Wortstellung

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

⚠️ **CG-NAME1:** command_gauge EN-Namen stellen das Fenster ans Ende:
`Usage {window}` etc. — *Schließung:* mit CG-W2 auf `{window} <Konzept>`.

## 9. Ausnahmeregelung (⚠️-Regime)

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

## 10. Offene Kanon-Punkte (gelten für beide Integrationen)

| ID | Punkt | Stand |
|---|---|---|
| OP-1 | `suggested_object_id`-Pinning auf Englisch (Vorbild `ha-health-o-mat`) — beide Repos ohne Pinning; command_gauge hat deutsch Erstregistrierte Slugs (0.1.1) | Koordinierte Umsetzung + Registry-Migration geplant |
