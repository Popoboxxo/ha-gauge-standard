# ha-gauge-standard — Gauge Entity Canon (Single Source of Truth)

**Meta-/Standard-Repo** für die *Gauge*-Familie von Home-Assistant-HACS-Integrationen.
Es enthält **keinen Integrations-Code**, sondern den verbindlichen **Gauge Entity Canon**:
die Spezifikation, damit alle Gauge-Integrationen für Enduser **gleich aussehen und
gleich funktionieren** — gleiche Entity-Namen, gleiche Attribute, gleiche
Einheiten/Device-Classes/Icons, gleiche Optionen.

> Interne Doku, daher Deutsch; fachliche Schlüsselbegriffe bleiben Englisch
> (*entity canon*, *translation key*, *device class*, …).

## Rolle

| Aspekt | Festlegung |
|---|---|
| **Single Source of Truth** | `canon/entities.md` (menschlich lesbar) + `canon/entities.schema.json` (maschinenlesbar) definieren verbindlich, wie Gauge-Entities heißen und aussehen. |
| **Master/Stil-Referenz** | [`ha-go-gauge`](https://github.com/Popoboxxo/ha-go-gauge) — wo sich Integrationen unterscheiden, gilt `go_gauge` **2.0.0** als Kanon-Entscheidung, sofern unten nicht anders festgelegt. |
| **Consumer** | [`ha-go-gauge`](https://github.com/Popoboxxo/ha-go-gauge) (`go_gauge`) und [`ha-command-gauge`](https://github.com/Popoboxxo/ha-command-gauge) (`command_gauge`). `command_gauge` ist das aktive **Konvergenz-Ziel**. |
| **Paar-Change-Pflicht** | Jede Kanon-Änderung ist ein **Paar-Change**: sie wird in beiden Integrationen umgesetzt (soweit die jeweilige API hergibt) — nie nur in einem Repo. |
| **Ausnahmen** | Domain-begründete Divergenz ist nur mit ⚠️-Eintrag im Kanon erlaubt, inkl. Begründung und **Schließungsbedingung** (*closing condition*). |

## Inhalt

```
canon/
  entities.md          # verbindlicher Kanon v1.6.0 (menschenlesbar, Deutsch)
  entities.schema.json # maschinenlesbare Version (prüfbar)
scripts/
  check_canon.py       # Prüft eine Integration gegen entities.schema.json
matrix/
  parity.md            # Feature-Matrix / Pflegedatei (Kanon-Zustand)
```

## Nutzung der Consumer-Repos

- **Einbindung als Git-Submodule (geplant):** Beide Integrations-Repos binden
  `ha-gauge-standard` als Submodule ein (z. B. unter `external/ha-gauge-standard/`)
  und rufen `scripts/check_canon.py` in ihrer CI gegen den eigenen
  `custom_components/<domain>`-Baum auf. Bis die Submodule eingerichtet sind,
  wird der Checker lokal gegen die Checkout-Pfade der beiden Repos ausgeführt:

  ```bash
  # Referenz muss grün sein (Exit 0, keine Warnungen)
  python scripts/check_canon.py C:/Repositories/ha-go-gauge

  # Konvergenz-Ziel: Exit 0, ⚠️-Warnungen nur für registrierte Abweichungen
  python scripts/check_canon.py C:/Repositories/ha-command-gauge
  ```

- **Exit-Codes:** `0` = OK, `1` = Fehler. Warnungen (⚠️) für im Kanon
  registrierte Abweichungen lassen den Lauf grün.

## Git-Hooks (pre-commit)

Repo-Hooks via [pre-commit](https://pre-commit.com/)-Framework (`.pre-commit-config.yaml`):
JSON/Doc-Konsistenz (`scripts/check_docs.py`), Whitespace/EOF, YAML und
Conventional-Commits (`scripts/check_commit_msg.py`). Setup per Machine:

```bash
pip install pre-commit
pre-commit install --hook-type commit-msg
```

CI (`canon.yml`) additionally runs the Checker against both Consumer-Repos.

## Wartung

1. **Kanon ändern = zuerst hier.** Änderung an `canon/entities.md` und
   `canon/entities.schema.json` geht immer vor der Umsetzung in den
   Integrationen (Spec-first).
2. **Paar-Change über beide Integrationen** — dieselbe Änderung im selben
   Release-Zyklus in `ha-go-gauge` und `ha-command-gauge` ausliefern
   (siehe `matrix/parity.md`, Verfahren).
3. **API-blockierte Differenzen** (⚠️) nie durch synthetische Nachbildungen
   „schließen", sondern mit Schließungsbedingung dokumentieren und bei jedem
   Release auf „inzwischen umsetzbar?" prüfen.
4. **Entity-Breaking = MAJOR** in dem Repo, in dem es passiert
   (`unique_id` nie ändern; Renames nur per Entity-Registry-Migration).
5. Nach Kanon-Änderung: Checker gegen beide Repos laufen lassen —
   Referenz grün, Konvergenz-Ziel nur mit registrierten ⚠️.

## Sprachregeln

| Kontext | Sprache |
|---|---|
| User-Kommunikation & interne Doku | Deutsch |
| `strings.json` / `translations/en.json` (Master) | Englisch |
| Code & Commits (Conventional Commits) | Englisch |

## Status

Kanon **v1.6.0** — abgeleitet aus `go_gauge` **2.0.0** (Master). Neu in v1.6.0:
Der Kanon hebt den Konto-Vertrag auf eine **eigene Konto-ConfigEntry**
(`canon/entities.md` §13). Anlass: Der bisherige Text beschrieb die
Konto-Entities als „Catalog Owner / erste Workspace-Instanz" — real besitzt
go_gauge seit 2.0.0 eine workspace-unabhängige Konto-Entry
(`entry_kind: "account"`, `unique_id: go_gauge_account`, Device `Go Gauge Konto`
mit `identifiers: {(DOMAIN, "account")}`); die Catalog-Owner-Regel entfällt
ersatzlos. Verbindlich sind damit **8 Konto-Entities** mit `unique_id`-Präfix
`account_` (5 Katalog/Status + Button + Switch + Number), ein **accountweiter,
evidenz-/TTL-basierter** `api_reachable` (Tri-State: frischer Erfolg → ON,
neutrale Antwort `no_subscription`/`auth_error` → unknown, nur frische Fehler →
OFF, keine frische Evidenz → unknown; TTL 2× Konto-Intervall / 3×
Usage-Intervall), der **device-scoped Refresh-Split** (geteilter
`translation_key` `refresh`: Workspace = nur Usage-Zyklus, Konto = nur
Katalog-Fetch) und die **globalen Modell-Settings** auf der Konto-Entry
(`auto_update_models` Default ON, `models_refresh_min` 1–1440 / Default 60).
HA-Mindestversion **2026.8.0**; Migration **v7 → v8** setzt `entry_kind`, die
`unique_id`-Umschreibung erfolgt im Adoption-Sweep, Alt-Settings-Entities
werden entfernt — `entity_id`/History bleiben erhalten. `command_gauge` bleibt
**unberührt** (1 Entry = 1 Konto, kein Konto-Split). Kein neuer ⚠️-Eintrag —
CG-D1 bleibt als Doku-Info (command_gauge ohne Konto-Entry) bestehen.
Neu in v1.5.0: Der Kanon regelt normativ den **Config-Flow für die
Token-Erneuerung (Reauth)**
(`canon/entities.md` §12): 401 → `ConfigEntryAuthFailed` (typisierter Auth-Status,
kein transienter Netzwerkfehler), `async_step_reauth` → `async_step_reauth_confirm`
mit Austausch **nur** des Secrets (`unique_id`/`entry_id` unverändert),
Setup-Re-Raise nach `hass.data`-Cleanup, i18n-Pflicht für `reauth_confirm` +
Abort-Gründe, kein `VERSION`-Bump und strukturelle Auth-Abbildung im Status-Sensor
(`auth_error`, §4). 403 EntitlementError bleibt `no_subscription` (kein Auth-Fall).
Kein neuer ⚠️-Eintrag — command_gauge **1.2.0** ist konforme Referenz, go_gauge
zieht mit **PR #32** nach (gemergt 2026-10-18). Neu in v1.4.0:
**command_gauge 1.2.0** implementiert den Scope-Status-Sensor `api_status`
(⚠️ CG-B5 geschlossen) — abgeleitet aus dem Per-Sektion-Status, dem Abo-Status
und den Fenster-`exceeded`-Flags (siehe `canon/entities.md` §4). Neu in v1.3.1:
**command_gauge 1.1.1** korrigiert die synthetische `month`-Ableitung (⚠️ CG-M1,
siehe `canon/entities.md` §2): `cap` ist der **Plan-Grant** aus dem Plan-Katalog
(gekeyt über die Subscription-`planId`), `used = max(0, cap −
credits.monthly_credits)` (die API liefert nur die *verbleibenden* Monats-Credits)
und `reset = subscription.period_end`. Neu in v1.3: **command_gauge 1.1.0**
ergänzt das `month`-Fenster mit dem vollen 7er-Satz (+ `rate_limited`) —
**synthetisch**, weil die CommandCode-API kein rollierendes Monatsfenster
liefert (`windowLimits` nur `fiveHour`/`weekly`). Die Fenster-Reihenfolge ist
damit kanonisch; die frühere `windows`-Abweichung entfällt, die synthetische
Ableitung ist als ⚠️ CG-M1 registriert (siehe `canon/entities.md` §2).

Kanon v1.2: **command_gauge 1.0.0** vollzog die Kanon-Konvergenz —
`translation_keys`, `{window}`-Wortstellung, Icons, `usage`-Status/Attribute,
`model_catalog`, `subscription_active` (ohne `device_class`) und Settings-Keys
sind kanonisch; Alias-Keys entfielen, Legacy-`unique_id`-Suffixe wurden per
Entity-Registry-Migration umgeschrieben (Historie bleibt). Kanon v1.1:
Scope-Status-Sensor `api_status` (go_gauge 1.6.0), `subscription_active` ohne
device_class.

Registriert bleiben nur **API-blockierte** Abweichungen (Pricing-Katalog-Sensoren/
Attribute), die **synthetische** month-Ableitung (CG-M1) und **domain-begründete**
Number-Ranges.

Checker-Ergebnis: `check_canon.py` → go_gauge **0/0** (Referenz grün),
command_gauge **0 Fehler / 8 registrierte Warnungen**.
