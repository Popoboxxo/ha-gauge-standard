# Gauge Entity Canon v1.7.0

Verbindliche Spezifikation des Entity-Modells aller Gauge-Integrationen
(`go_gauge`, `command_gauge`). Master/Stil-Referenz: **ha-go-gauge 2.0.0**.
Abweichungen sind nur als registrierter ⚠️-Eintrag erlaubt
(→ Abschnitt „Ausnahmeregelung").

> **Neu in Kanon v1.7.0 (2026-10-25):** Der Kanon wird um einen **getrennten,
> verbindlichen Repository-Hygiene-/Dokumentations-Contract** ergänzt
> (`canon/repository.md` + `canon/repository.schema.json`, geprüft von
> `scripts/check_repo_hygiene.py`). Er regelt ausschließlich die
> Repository-Oberfläche (README-Paar EN/DE, My-Link, Screenshot, `hacs.json`/
> `manifest.json`/Brand-Asset, Tag↔Manifest-Sync, Community-Dateien, CI-Gates,
> Releases). **Der Entity-Inhalt dieses Dokuments bleibt unverändert**
> (Master `go_gauge` 2.0.0, `master.version` 2.0.0; go_gauge 2.0.2 ist rein
> Doku/Metadaten). `command_gauge` ist im Hygiene-Contract **⚠️ offen**
> (Transition) — **kein Entity-Bruch und kein neuer CG-Eintrag**.

> **Neu in Kanon v1.6.0 (2026-10-25):** Der Kanon hebt den Konto-Vertrag auf eine
> **eigene Konto-ConfigEntry** (go_gauge **2.0.0**). Anlass: Der bisherige Text
> beschrieb die Konto-Entities als „Catalog Owner / erste Workspace-Instanz" —
> real besitzt go_gauge seit 2.0.0 eine eigene, workspace-unabhängige
> Konto-ConfigEntry (`entry_kind: "account"`, `unique_id: go_gauge_account`),
> der Device `Go Gauge Konto` (`identifiers: {(DOMAIN, "account")}`) gehört ihr.
> Die **Catalog-Owner-Regel entfällt ersatzlos**; Konto-Entities tragen das
> `unique_id`-Präfix `account_` (§13). Neu verbindlich außerdem:
> `api_reachable` ist accountweit und **evidenz-/TTL-basiert** (Tri-State, §5),
> die beiden Refresh-Buttons sind **device-scoped** geteilt (`translation_key`
> `refresh`: Workspace = nur Usage-Zyklus, Konto = nur Katalog-Fetch, §8.3),
> und die Modell-Settings (`auto_update_models`, `models_refresh_min`) sind
> **global auf der Konto-Entry** (Default ON / 60 min, Range 1–1440). HA-Minimum
> ist **2026.8.0**; die Schema-Migration **v7 → v8** erhält `entity_id`/History
> (§13). `command_gauge` bleibt **unberührt** (kein Konto-Split: dort gilt
> weiter 1 Entry = 1 Konto). **Kein neuer ⚠️-Eintrag** — CG-D1 bleibt als
> Doku-Info bestehen.

> **Neu in Kanon v1.5.0 (2026-10-18):** Der Kanon regelt erstmals den
> **Config-Flow für die Token-Erneuerung (Reauth)** normativ (§12). Anlass: Ein
> abgelaufener Token (HTTP 401) ließ Entities ohne Reauth-Flow dauerhaft auf
> `error`/`unavailable` stehen. Neu verbindlich: typisierter Auth-Status im
> Coordinator (401 → `ConfigEntryAuthFailed`, **kein** transienter Netzwerkfehler;
> 403 EntitlementError bleibt `no_subscription`), `async_step_reauth` →
> `async_step_reauth_confirm` mit Austausch **nur** des Secrets (`unique_id` und
> `entry_id` unverändert), Re-Raise nach `hass.data`-Cleanup im Setup,
> i18n-Pflicht für `reauth_confirm` + Abort-Gründe, kein `VERSION`-Bump und
> strukturelle Auth-Abbildung im Status-Sensor (`auth_error`, §4).
> Referenzimplementierung: command_gauge **1.2.0**; go_gauge zieht mit
> **PR #32** nach (gemergt 2026-10-18). **Kein neuer ⚠️-Eintrag** — die Angleichung ist
> beschlossen (Paar-Change), keine domain-begründete Divergenz.

> **Neu in Kanon v1.4.0 (2026-10-15):** command_gauge **1.2.0** implementiert
> den Scope-Status-Sensor `api_status` (§4) und schließt damit die Abweichung
> **CG-B5**. Die CommandCode-API liefert den Abo-/API-Status zwar nur
> konto-weit, aber command_gauge leitet den Kanon-Enum aus seinem
> Per-Sektion-Status (`section_status`), dem Abo-Status und den
> Fenster-`exceeded`-Flags ab (`auth_error` bei 401, `no_subscription` bei
> inaktivem Abo, `api_error` bei sonstigem Sektionsfehler, `rate_limited` bei
> überschrittenem Fenster, sonst `ok`). command_gauge hat genau einen Scope pro
> Config-Entry.

> **Neu in Kanon v1.3.1 (2026-10-14):** Die synthetische `month`-Ableitung
> (⚠️ CG-M1, siehe §2) wurde korrigiert. `cap` ist der **Plan-Grant** aus dem
> Plan-Katalog (gekeyt über die Subscription-`planId`) und
> `used = max(0, cap − credits.monthly_credits)` — `credits.monthlyCredits` ist
> ein **Rest-Betrag**, kein Grant (die 1.1.0-Ableitung nutzte ihn fälschlich als
> `cap`, wodurch der Prozentwert mit schwindendem Grant stieg). Umsetzung:
> command_gauge **1.1.1**.

> **Neu in Kanon v1.3 (2026-10-08):** command_gauge **1.1.0** füllt die
> `month`-Fensterdimension mit dem vollen 7er-Satz — aber **synthetisch** aus dem
> Monats-Credit-Grant abgeleitet, weil die CommandCode-API kein rollierendes
> Monatsfenster liefert (⚠️ CG-M1, siehe §2). Die Fenster-Reihenfolge ist damit
> kanonisch; die frühere `windows`-Abweichung entfällt.

> **Seit Kanon v1.2 (2026-10-06):** `command_gauge` **1.0.0** hat die Konvergenz
> vollzogen — `translation_keys`, `{window}`-Wortstellung, Icons, `usage`-Status/
> Attribute, `model_catalog`, `subscription_active` (ohne `device_class`) und die
> Settings-Keys sind kanonisch; die Legacy-Alias-Keys sind entfallen und die
> Legacy-`unique_id`-Suffixe wurden per Entity-Registry-Migration auf die
> Kanon-Suffixe umgeschrieben (Historie bleibt erhalten). Registriert sind nur
> noch **API-blockierte** (Pricing-Katalog) und **domain-begründete**
> (Number-Ranges) Abweichungen.

Maschinenlesbare Version: `canon/entities.schema.json`
(diese Datei ist die normative Referenz bei Widersprüchen).

## 1. Device-Topologie

| Aspekt | Kanon |
|---|---|
| Device pro Config-Entry, identifiziert via `identifiers: {(DOMAIN, entry.entry_id)}` | verbindlich |
| Device-Name | `f"{Brand} {Scope}"` — go_gauge: `Go Gauge {workspace_name}`; command_gauge: `Command Gauge {account_name}` |
| `manufacturer` | `Popoboxxo` (beide Integrationen) |
| `model` | API-Produktname — go_gauge: `OpenCode Go`; command_gauge: `CommandCode Cloud` |
| Account-Device (konto-/workspace-übergreifende Entities) | go_gauge: separates Device `Go Gauge Konto` mit `identifiers: {(DOMAIN, "account")}`, owned by the **eigene Konto-ConfigEntry** (`entry_kind: "account"`, `unique_id: go_gauge_account`) — **kein Catalog Owner** mehr, keine erste Workspace-Instanz; die Konto-Entities tragen das `unique_id`-Präfix `account_` (§13). command_gauge: entfällt (jeder Entry = eigenes Konto, kein Duplikat-Problem) ⚠️ CG-D1 |
| `_attr_has_entity_name = True` global; kein `_attr_name`-Literal irgendwo | verbindlich (HACS-eiserne Regel) |

## 2. Fenster (Windows)

| Fenster | Label (EN, `WINDOW_LABELS`) | Nominaldauer (`WINDOW_SECONDS`) |
|---|---|---|
| `5h` | `5h rolling` | 18 000 s |
| `week` | `Weekly` | 604 800 s |
| `month` | `Monthly` | 2 592 000 s (30-Tage-Näherung) ⚠️ CG-M1 (synthetisch) |

Fenster-Labels werden als `{window}`-Placeholder in `translation_placeholders`
gesetzt; die Fenster-Entities werden dynamisch aus der Fenster-Liste erzeugt
(deshalb skaliert der 7er-Satz automatisch auf neue Fenster).

⚠️ **CG-M1 (command_gauge, synthetisch):** Die CommandCode-API hat **kein**
rollierendes Monatsfenster — `windowLimits` liefert nur `fiveHour`/`weekly`;
das in der UI gezeigte „Monthly Limit" ist der **Credit-Grant pro
Billing-Zyklus**. Das Kanon-`month`-Fenster wird in command_gauge daher
**synthetisch abgeleitet**:

- `cap` = Plan-Grant (USD) aus dem Plan-Katalog, gekeyt über die
  Subscription-`planId` (z. B. `individual-go` = $10, `individual-goat` = $70,
  `individual-pro-v1` = $80)
- `used` = `max(0, cap − credits.monthly_credits)` (Spend aus dem Grant;
  `credits.monthlyCredits` ist ein **Rest-Betrag**, nicht der Grant)
- `reset` = `subscription.period_end` (Billing-Zyklus)

Hintergrund: `/alpha/billing/credits` liefert nur die *verbleibenden*
Monats-Credits, der Grant steht nicht in der API. Die Ableitung spiegelt die
offizielle `command-code`-CLI (Plan-Katalog, `(grant − remaining) / grant`). Bei
unbekanntem Plan oder fehlendem Restbetrag liefert die Ableitung `None` (nie
eine Fake-Zahl); der Reset-Bezug ist optional (`period_start` wird von der API
nicht garantiert). go_gauge liest `month` dagegen **direkt** aus der
OpenCode-API (`usage.monthly`). *Schließung:* entfällt (dokumentierte
synthetische Ableitung); bei echtem API-Monatsfenster `WINDOW_API_KEYS`
erweitern und die Synthese entfernen.

## 3. Fenster-Sensor-Satz (7er-Satz, je Fenster)

Pro Fenster existieren exakt diese 7 Sensoren. `unique_id`-Schema:
`f"{entry.entry_id}_{scope}_{window}_{suffix}"` (scope = workspace_key).
Workspace-unabhängige Konto-Entities folgen dagegen dem Präfix-Schema
`account_<suffix>` (§13). Reihenfolge der Suffixe ist Kanon.

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

✅ **CG-B5 (command_gauge, geschlossen in 1.2.0):** command_gauge implementiert
`api_status` jetzt — abgeleitet aus dem Per-Sektion-Status (`section_status`),
dem Abo-Status und den Fenster-`exceeded`-Flags. Die CommandCode-API liefert den
Abo-/API-Status zwar nur konto-weit (`subscription.status`: active/trialing/
paid/…), aber command_gauge hat genau einen Scope pro Config-Entry, sodass die
Ableitung kanon-konform ist: `401` → `auth_error`, inaktives Abo →
`no_subscription`, sonstiger Sektionsfehler → `api_error`, überschrittenes
Fenster → `rate_limited`, sonst `ok`.

## 5. Binary Sensoren

| Konzept | translation_key | device_class | Icon | unique_id-Suffix | Attribute | EN-Name |
|---|---|---|---|---|---|---|
| Rate Limited (je Fenster) | `rate_limited` | PROBLEM | `mdi:block-helper` | `limited` | — | `{window} rate-limited` |
| Subscription Active (je Scope) | `subscription_active` | — (keine) | `mdi:shield-check-outline` | `subscription_active` | `workspace_key`, `note` | `Subscription Active` |
| API Reachable (konto-weit) | `api_reachable` | CONNECTIVITY | — (HA-Default) | `api_reachable` | — | `API Reachable` |

Verhalten: `rate_limited` ON bei Fenster-Status `rate-limited`; bei
`no_subscription`/Update-Fehler `unavailable` (nicht OFF).
`subscription_active` ON bei Scope-Status `ok`, OFF bei `no_subscription`
(Attribut `note` trägt die Ursache), sonst `unknown` (None). **Kein
device_class** (Kanon seit 1.6.0): CONNECTIVITY ließ HA den Zustand als
„Getrennt" rendern — ein Abo ist ein Subskriptionszustand, keine Verbindung;
Verbindung ist allein Sache von `api_reachable`.

### 5.1 `api_reachable` (go_gauge): accountweit, evidenz-/TTL-basiert

Verbindlich für go_gauge **2.0.0**. Der Sensor gehört der Konto-Entry
(`unique_id` `account_api_reachable`), ist **accountweit** (nicht je Workspace)
und **tri-state** — er leitet den Zustand aus zeitgestempelten Fetch-Ergebnissen
(*Evidence*) ab, nicht mehr aus `last_update_success` + `fetched_at`:

| Beobachtung | Ergebnis |
|---|---|
| mindestens ein **frischer** Erfolg (Katalog-Fetch `ok` **oder** Workspace-`status=ok`) | **ON** (`fresh_ok`) |
| frische *neutrale* Antwort (401 → `auth_error`, 403 → `no_subscription`) ohne frischen Erfolg | **unknown** (`answered_no_success`) — neutral zählt **nicht** als Erfolg |
| nur frische Fehler (Netz/5xx/Cloudflare) | **OFF** (`all_fresh_failed`) |
| keine frische Evidence (auch leer) | **unknown** (`no_evidence`) |

- **Evidenzquellen:** Konto-Katalog-Fetch (`source="models"`, `workspace=None`)
  und jeder geladene Workspace-Zyklus (`source="usage"`, mit Workspace-Name).
- **TTL:** Models-Evidenz lebt **2× Konto-Intervall** (bei ausgeschaltetem
  Auto-Refresh 2× Default 60 min = 120 min, da es kein Basis-Intervall gibt),
  Usage-Evidenz **3× Workspace-Usage-Intervall**. Maßgeblich ist das
  *konfigurierte* Basis-Intervall, nicht das Backoff-erweiterte effektive —
  sonst hielte sich veraltete Evidenz unbegrenzt am Leben.
- **Grenzfall:** `age <= ttl` zählt als frisch; veraltete Evidenz wird ignoriert
  und **nie** als Fehler uminterpretiert.
- **Unit/device_class:** CONNECTIVITY, keine Unit, kein state_class.
- Attribute sind **nicht kanonisch gefordert** (`attributes: []`); go_gauge
  publiziert zusätzlich `reachability_reason`, `evidence`, `models_ttl_s`,
  `usage_ttl_s`, `checked_at` (rein informativ, command_gauge nicht).

command_gauge nutzt weiterhin das Alias-Verhalten (`is_on` = `last_update_success`
+ `fetched_at`, bewusst immer `available`) — Konto-Sensor ohne Konto-Entry.

✅ **CG-B1/B2/B3 (command_gauge, geschlossen in 1.0.0):** `rate_limited` ist
kanonisch (Icon `mdi:block-helper`, Suffix `limited`, `unavailable` statt OFF
ohne Abo); in command_gauge ist `api_reachable` kanonisch benannt (`is_on` =
`last_update_success` + `fetched_at`, bewusst weiterhin immer `available` —
Konto-Sensor ohne Konto-Entry; go_gauge nutzt seit 2.0.0 die Evidenz-/TTL-Regel
aus §5.1); der
`subscription_active`-Sensor hat **keinen** `device_class` mehr und trägt
`mdi:shield-check-outline` plus `workspace_key`/`note`.
⚠️ **CG-B4 (domain-spezifisch, erlaubt):** `credits_below_threshold`
(PROBLEM, ON wenn Guthaben unter API-Schwelle) — command_code Credit-Modell,
kein go_gauge-Äquivalent. *Schließung:* entfällt.

## 6. Katalog-Sensoren (Modell-Katalog)

Grundsatz: **EIN Sensor trägt den kompletten Katalog als dynamische
JSON-Attribute** — neue Modelle erscheinen ohne neue Entities.

Besitz (go_gauge seit 2.0.0): Die vier Katalog-Sensoren gehören der **eigenen
Konto-ConfigEntry** (`entry_kind: "account"`), nicht mehr einer Workspace-Entry
und nicht mehr einem „Catalog Owner". Sie hängen am Device
`Go Gauge Konto` (`identifiers: {(DOMAIN, "account")}`) und tragen das
`unique_id`-Präfix **`account_`** — z. B. `account_model_catalog`,
`account_models_live_count`, `account_cheapest_model`, `account_free_models`
(§13). Der in der Tabelle genannte `unique_id`-Suffix bleibt der nackte
Konzept-Token; das `account_`-Präfix ist die Device-Bindung der Konto-Entry.

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

go_gauge publiziert auf `model_catalog` zusätzlich die Konto-Settings als
Attribute (`account_auto_update_models`, `account_fetch_interval_minutes`,
`account_models_refresh_minutes`, `account_last_models_outcome`) — rein
informativ, **nicht** kanonisch gefordert (command_gauge liefert sie nicht).

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

| # | translation_key | Unit | Min | Max | Default | Icon | unique_id-Suffix | EN-Name | Ebene |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `warning_threshold` | `%` | **1** | **100** | 80 | `mdi:alert-octagon-outline` | `warn_percent` | `Warning Threshold` | Workspace |
| 2 | `pace_red_limit` | `%` | **1** | **300** | 100 | `mdi:alert-decagram-outline` | `pace_red_percent` | `Pace Red Limit` | Workspace |
| 3 | `usage_refresh_min` | `min` | **1** | **1440** | 10 | `mdi:timer-outline` | `usage_refresh_minutes` | `Usage Refresh (min)` | Workspace |
| 4 | `models_refresh_min` | `min` | **1** | **1440** | 60 | `mdi:timer-outline` | `models_refresh_minutes` | `Models Refresh (min)` | **Konto (global)** |

Die Schwellen gelten einheitlich für ALLE Fenster (nicht je Fenster).
Defaults zusätzlich als Konstanten: `DEFAULT_WARN_PERCENT=80`,
`DEFAULT_PACE_RED_PERCENT=100`, `DEFAULT_USAGE_REFRESH_MINUTES=10`,
`DEFAULT_MODELS_REFRESH_MINUTES=60`.

**go_gauge 2.0.0 — Modell-Settings sind global (Konto-Entry):**
`models_refresh_min` ist **kein** Workspace-Setting mehr. Es gehört der
Konto-ConfigEntry, hängt am Konto-Device und heißt `account_models_refresh_minutes`
(§13). Range **1–1440**, Default **60** (Konstanten `ACCOUNT_MODELS_REFRESH_MIN`/
`_MAX`, `DEFAULT_ACCOUNT_MODELS_REFRESH_MINUTES=60`). Wirkung: `set_fetch_interval()`
armiert den Katalog-Timer neu + `persist_account_options` — ohne Entry-Reload
und ohne `recalculate_interval()`, weil der Konto-Koordinator einen eigenen
Fetch-Timer besitzt. Die drei Workspace-Numbers (`warning_threshold`,
`pace_red_limit`, `usage_refresh_min`) bleiben unverändert workspace-lokal
(`persist_options`).

✅ **CG-N1 (Keys/Icons geschlossen in 1.0.0):** command_gauge nutzt jetzt die
Kanon-Keys `warning_threshold`, `pace_red_limit`, `usage_refresh_min`,
`models_refresh_min` mit den Kanon-Icons (`mdi:alert-octagon-outline`,
`mdi:alert-decagram-outline`, `mdi:timer-outline`). ⚠️ **domain-begründete Ranges bleiben:** `pace_red_limit` 1–**1000** ⚠️ CG-N2 (Forecast darf >300 projizieren),
`usage_refresh_min` Min **5** ⚠️ CG-N3 und `models_refresh_min` Min **60** ⚠️ CG-N4
(CommandCode-API-Fair-Use). *Schließung:* entfällt (domain-begründet).

### 8.2 Switches (2)

| translation_key | Icon | unique_id-Suffix | EN-Name | Ebene |
|---|---|---|---|---|
| `auto_update_usage` | `mdi:autorenew` | `auto_update_usage` | `Auto Update Usage` | Workspace |
| `auto_update_models` | `mdi:autorenew` | `auto_update_models` | `Auto Update Models` | **Konto (global)** |

`auto_update_usage` (workspace-lokal, go_gauge/command_gauge): schaltet den
Usage-Zyklus, triggert `recalculate_interval()`, persistiert via
`persist_options`.

`auto_update_models` (go_gauge 2.0.0: **global auf der Konto-Entry**, Default
**ON**, `unique_id` `account_auto_update_models`): schaltet den Katalog-Zyklus
über `set_auto_fetch()` **live** und persistiert via `persist_account_options` —
**kein** `recalculate_interval()`, kein Entry-Reload (die Konto-Entry hat
bewusst keinen Update-Listener). Die frühere per-Workspace-Instanz dieses
Schalters entfällt; ihre Alt-Entities werden entfernt (§13).

✅ **CG-S1 (geschlossen in 1.0.0):** command_gauge nutzt `auto_update_usage` /
`auto_update_models` (Icons identisch, unique_id-Suffix kanonisch) — dort
weiterhin beide auf der jeweiligen Entry, ohne Konto-Split.

### 8.3 Buttons (2, geteilter `translation_key`)

Beide Buttons heißen kanonisch `Refresh` — derselbe `translation_key`
(`refresh`), getrennt durch **Device** und `unique_id`-Präfix. Ein Klick löst
jeweils **nur** seinen eigenen Zyklus aus:

| translation_key | Icon | unique_id-Suffix | EN-Name | Ebene | Wirkung |
|---|---|---|---|---|---|
| `refresh` | `mdi:refresh` | `refresh` | `Refresh` | Workspace-Device | nur **Usage**-Zyklus (`last_usage_fetch = None` → `async_request_refresh()`) |
| `refresh` | `mdi:refresh` | `refresh` | `Refresh` | **Konto-Device** (`account_refresh`) | nur **Katalog-Fetch** (`AccountCoordinator.async_fetch_now()`, der einzige HTTP-Pfad der Konto-Entry) |

Der workspace-scoped Button darf **keinen** Katalog-Fetch auslösen (der Katalog
gehört der Konto-Entry), der Konto-Button **keinen** Usage-Zyklus. Die
Trennung ist device-scoped: gleicher Anzeigename, unterschiedliche
`unique_id` (`{entry_id}_refresh` vs. `account_refresh`).

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

## 12. Config-Flow-Kanon: Token-Erneuerung (Reauth)

Verbindlich für beide Integrationen. Anlass: Ein abgelaufener Token führte ohne
Reauth-Flow dazu, dass Entities dauerhaft auf `error`/`unavailable` stehen
blieben; HA sieht dafür den Reauth-Flow vor (`ConfigEntryAuthFailed` →
`async_step_reauth`).

### 12.1 Coordinator: Auth-Fehler typisieren (401 ≠ transient)

- HTTP **401** ist ein Auth-Fehler und wird als
  `homeassistant.exceptions.ConfigEntryAuthFailed` **geworfen** — über eine
  typisierte Statusmenge (z. B. `AUTH_STATUSES = {401}`).
- **Nicht** als transientes Netzwerkproblem behandeln (`UpdateFailed`).
- HTTP **403** mit `EntitlementError` ist **kein** Auth-Fall und bleibt
  `no_subscription` (vgl. §4); er löst **keinen** Reauth-Flow aus.

### 12.2 Config-Flow: `async_step_reauth` → `async_step_reauth_confirm`

- `async_step_reauth` (Trigger durch `ConfigEntryAuthFailed` bzw.
  „Erneut authentifizieren" in der UI) delegiert an `async_step_reauth_confirm`.
- Im Confirm-Schritt wird **ausschließlich das Secret** (Token/API-Key) ersetzt:
  `entry.unique_id` und `entry.entry_id` bleiben **unverändert** (eiserne Regel
  „`unique_id` nie ändern").
- Abort-Gründe sind kanonisch: `reauth_failed` (Entry nicht auffindbar) und
  `reauth_successful` (Token ersetzt + Entry neu geladen).

### 12.3 Setup: `ConfigEntryAuthFailed` nicht verschlucken

- `async_setup_entry` darf `ConfigEntryAuthFailed` aus dem ersten Refresh
  **nicht** abfangen und als generischen Setup-Fehler behandeln.
- Nach dem Aufräumen von `hass.data` wird die Exception **erneut geworfen**
  (`raise`), damit HA den Reauth-Flow anbietet.

### 12.4 i18n-Pflicht

- Der Schritt `reauth_confirm` sowie die Abort-Gründe `reauth_failed` /
  `reauth_successful` stehen in `strings.json` **und** in allen
  `translations/*.json`.
- Die Key-Parität bleibt grün (CI-Check `scripts/check_json_consistency.py` in
  den Integrationen).

### 12.5 Kein `VERSION`-Bump

- Der Reauth-Flow ändert **kein** Entry-Schema → **kein** `VERSION`-Bump und
  **kein** `async_migrate_entry`-Handler (eiserne Regel Releases).

### 12.6 Tests (Pflicht)

- 401-Response → `ConfigEntryAuthFailed` (nicht `UpdateFailed`).
- Reauth-Confirm ersetzt nur das Token; `unique_id`/`entry_id` bleiben stabil.
- 403-Entitlement bleibt `no_subscription` (kein Reauth-Trigger).

### 12.7 Status-Sensor: Auth-Fehler strukturell abbilden

- Auth-Fehler werden **strukturell** über den Scope-Status abgebildet
  (Kanon-State `auth_error`, vgl. §4), **nicht** per String-Matching auf
  Fehlertexte.

**Referenz:** command_gauge **1.2.0** = konforme Referenzimplementierung
(Reauth vollständig); go_gauge zieht mit **PR #32** nach (gemergt 2026-10-18).

## 13. Konto-ConfigEntry (go_gauge 2.0.0)

Verbindlich für den Master. Seit go_gauge **2.0.0** besitzt die Integration
**eine** workspace-unabhängige **Konto-ConfigEntry** neben N Workspace-Entries:

| Aspekt | Kanon |
|---|---|
| Entry-Art | `data["entry_kind"] == "account"` (Workspaces: `"workspace"`); fehlt der Key, gilt `"workspace"` (Alt-Entries) |
| `unique_id` | fest `go_gauge_account` (`ACCOUNT_ENTRY_UNIQUE_ID`) + Duplikat-Schutz — genau eine Konto-Entry pro Instanz |
| Titel | `Go Gauge Konto` (`ENTITY_NAME_ACCOUNT`) = Device-Name; kein Token, kein Secret, kein API-Zugriff beim Anlegen (auth-frei) |
| Device | `identifiers: {(DOMAIN, "account")}`, `manufacturer: Popoboxxo`, `model: OpenCode Go` |
| Abgrenzung | **Ersetzt die frühere „Catalog Owner / erste Workspace-Instanz"-Regel ersatzlos** — Konto-Entities hängen an keiner Workspace-Entry mehr |
| HA-Mindestversion | **2026.8.0** (`hacs.json`); Integration `version` **2.0.0** |

### 13.1 Die 8 Konto-Entities

Alle mit `unique_id`-Präfix **`account_`** (`ACCOUNT_UNIQUE_ID_PREFIX`), alle am
Konto-Device, keiner Workspace-Entry zugeordnet:

| # | Entity | Plattform | translation_key | unique_id | Kanon-Abschnitt |
|---|---|---|---|---|---|
| 1 | Model Catalog | sensor | `model_catalog` | `account_model_catalog` | §6 |
| 2 | Live Models Count | sensor | `live_models_count` | `account_models_live_count` | §6 |
| 3 | Cheapest Model | sensor | `cheapest_model` | `account_cheapest_model` | §6 |
| 4 | Free Models | sensor | `free_models` | `account_free_models` | §6 |
| 5 | API Reachable | binary_sensor | `api_reachable` | `account_api_reachable` | §5.1 |
| 6 | Refresh | button | `refresh` | `account_refresh` | §8.3 |
| 7 | Auto Update Models | switch | `auto_update_models` | `account_auto_update_models` | §8.2 |
| 8 | Models Refresh (min) | number | `models_refresh_min` | `account_models_refresh_minutes` | §8.1 |

Verteilung: **5 Katalog/Status** (4 Sensoren + 1 Binary-Sensor), **1 Button**,
**1 Switch**, **1 Number**. Der Template-`unique_id`-Suffix bleibt jeweils der
nackte Konzept-Token (`model_catalog`, `refresh`, `models_refresh_minutes`, …);
`account_` ist das Präfix der Konto-Entry, kein Suffix-Bestandteil.

Nicht auf der Konto-Entry (bleiben workspace-lokal): der 7er-Fenstersatz, die
Fenster-`rate_limited`-Flags, `subscription_active`, `api_status`,
`warning_threshold`, `pace_red_limit`, `usage_refresh_min`, `auto_update_usage`
und der workspace-scoped Refresh-Button.

### 13.2 Migration v7 → v8 (Breaking, Historie bleibt)

- **`VERSION` 8 setzt `entry_kind`**: jede migrierte (Workspace-)Entry wird
  explizit als `workspace` markiert (idempotent via `setdefault`, O(1), kein
  Registry-/Netz-Zugriff); die Konto-Entry schreibt `account` bereits im
  Config-Flow.
- **`entity_id` und History bleiben erhalten** — die Migration legt keine
  Entity neu an und ändert keine `entity_id`.
- **`unique_id`-Umschreibung erfolgt im Adoption-Sweep.** Die früher auf einer
  Workspace-Entry registrierten Katalog-Entities werden auf die kanonischen
  `account_*`-IDs umgeschrieben (`async_update_entity(new_unique_id=...)`),
  behalten dabei ihre `entity_id` und werden auf die Konto-Entry und das
  Konto-Device umgehängt. Kollisionen: ein Gewinner wird adoptiert, ein
  Verlierer wird neutralisiert (deaktiviert, `unique_id` unangetastet), nicht
  gelöscht.
- **Alt-Settings-Entities werden entfernt**: die vormaligen
  `<workspace>_auto_update_models` / `<workspace>_models_refresh_minutes`
  werden aus der Entity-Registry entfernt (keine Wertübernahme) — die
  `account_*`-Settings sind explizit ausgenommen.
- Reihenfolge ist verbindlich: erst die Entity-ID-Migration (v7), dann die
  `entry_kind`-Markierung (v8); ein gescheiterter v7-Pass darf nicht auf v8
  springen.

### 13.3 Abgrenzung command_gauge

**`command_gauge` bleibt unberührt.** Dort gilt weiter **1 Config-Entry = 1
Konto**: es gibt keine Konto-Entry, keinen Konto-Split, keine
`account_`-Präfixe und keine v7→v8-Konto-Migration. Die Konto-Entities des
Kanons (§13.1) sind damit **go_gauge-spezifisch**; command_gauge bildet sie —
soweit die CommandCode-API es hergibt — auf seiner eigenen Entry ab
(⚠️ CG-C1/CG-C2 für die Pricing-Sensoren, ⚠️ CG-D1 als Doku-Info).
