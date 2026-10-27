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
| **Master/Stil-Referenz** | [`ha-go-gauge`](https://github.com/Popoboxxo/ha-go-gauge) — wo sich Integrationen unterscheiden, gilt `go_gauge` **2.1.0** als Kanon-Entscheidung, sofern unten nicht anders festgelegt. |
| **Consumer** | [`ha-go-gauge`](https://github.com/Popoboxxo/ha-go-gauge) (`go_gauge`) und [`ha-command-gauge`](https://github.com/Popoboxxo/ha-command-gauge) (`command_gauge`). `command_gauge` ist das aktive **Konvergenz-Ziel**. |
| **Paar-Change-Pflicht** | Jede Kanon-Änderung ist ein **Paar-Change**: sie wird in beiden Integrationen umgesetzt (soweit die jeweilige API hergibt) — nie nur in einem Repo. |
| **Ausnahmen** | Domain-begründete Divergenz ist nur mit ⚠️-Eintrag im Kanon erlaubt, inkl. Begründung und **Schließungsbedingung** (*closing condition*). |

## Inhalt

```
canon/
  entities.md            # Entity-Kanon v1.8.0 (menschenlesbar, Deutsch)
  entities.schema.json   # maschinenlesbare Entity-Version (prüfbar)
  repository.md          # Repository-Hygiene-/Doku-Contract v1.7.0 (Deutsch)
  repository.schema.json # maschinenlesbare Beschreibung des Hygiene-Contracts
scripts/
  check_canon.py         # Prüft eine Integration gegen entities.schema.json
  check_repo_hygiene.py  # ausführbarer Regelsatz des Hygiene-Contracts
matrix/
  parity.md              # Feature-Matrix / Pflegedatei (Kanon-Zustand)
```

Der Entity-Kanon (`canon/entities.md`) und der Repository-Hygiene-Contract
(`canon/repository.md`) sind **zwei getrennte, sich ergänzende Verträge**:
Ersterer regelt Entities/Übersetzungen, letzterer die Repository-Oberfläche
(README-Paar, My-Link, Metadaten, Community-Dateien, CI, Releases). Eine
Hygiene-Änderung berührt **keine** Entity und keine `unique_id`.

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

## Repository-Hygiene prüfen

`scripts/check_repo_hygiene.py` prüft die Repository-Oberfläche gegen
`canon/repository.md` + `canon/repository.schema.json` (nur Dateien, HA-frei,
Python-Standardbibliothek). Rollenverteilung: `canon/repository.schema.json`
**beschreibt** den Contract maschinenlesbar, der Checker ist der
**ausführbare Regelsatz** und damit die maßgebliche Instanz. Nicht jeder
Schema-Schlüssel wird 1:1 vom Code konsumiert (GitHub-Einstellungen wie
Description/Topics lassen sich aus einem Checkout nicht prüfen); weicht beides
voneinander ab, gilt der Checker.

```bash
# Referenz: muss grün sein (Exit 0, keine Findings)
python3 scripts/check_repo_hygiene.py /pfad/zu/ha-go-gauge

# Konvergenz-Ziel: alle Lücken als WARNING, Exit 0
python3 scripts/check_repo_hygiene.py /pfad/zu/ha-command-gauge --warn-only
```

- **Exit-Codes:** `0` = keine Fehler, `1` = mindestens ein Fehler **oder**
  unlesbarer/fehlender Repo-Pfad (letzteres bleibt auch mit `--warn-only`
  ein Fehler).
- **`--warn-only`** stuft jedes Finding zu einer Warnung herab und lässt den
  Lauf mit `0` enden — so bleiben Konvergenz-Ziele CI-grün, während die Lücken
  sichtbar bleiben.
- **`--schema PATH`** erzwingt eine abweichende Schema-Datei.
- Der Tag↔`manifest.version`-Abgleich ist best-effort: fehlt in einer flachen
  CI-Kopie die Tag-Info, meldet der Checker
  „Tag-Info nicht verfügbar — Tag↔Manifest nicht prüfbar“ als WARNING und
  **nie** als Fehler.

## Distribution: Custom Repository vs. Katalog

Der **Katalog-/Store-Eintrag ist optional**. Der **Custom-Repository-Weg über
den My-Link** (`hacs_repository`) ist ausdrücklich unterstützt und bleibt der
primäre Distributionspfad; der Hygiene-Contract gilt für beide Wege identisch.
`command_gauge` steht noch am Anfang der Transition (⚠️ offen: README-Paar,
`render_readme` in `hacs.json`, Community-Dateien); Schließungsbedingung:
„Hygiene-Contract umgesetzt (README EN/DE, Templates, Community-Dateien,
Checker grün)“. Das ist **keine Entity-Abweichung** und braucht keinen
CG-Eintrag.

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

Kanon **v1.8.0** — neue verbindliche **Entity-Kategorie-Policy** (§8.0):
Settings-Numbers und Auto-Update-Switches werden `entity_category: config`,
der Reset-Button bleibt `diagnostic`, Primärdaten und Refresh-Aktionen bleiben
`null`. Reine UI-/Registry-Metadaten: kein `unique_id`-, `entity_id`-, State-,
Historien- oder Automationsbruch. Beide Consumer haben die Werte übernommen;
der Checker erzwingt sie jetzt exakt.

Kanon **v1.7.0** — abgeleitet aus `go_gauge` **2.1.0** (Master). Neu in v1.7.0:
Aktivierung der in 1.6.0 nur reservierten **Burn-Lookback-Settings**
(`canon/entities.md` §8.4). Die drei Number-Slider (`burn_lookback_5h` /
`burn_lookback_week` / `burn_lookback_month`, `entity_category: config`, Steps
5/60/60, Defaults 120/720/2880) und der Reset-Button (`reset_burn_lookbacks`,
`entity_category: diagnostic`, `unique_id` `burn_lookback_reset`) sind jetzt
**Core-Entities** der `entities`-Liste: **27 Core-Entity-Einträge** (12 Sensoren,
3 Binary-Sensoren, **7 Numbers**, 2 Switches, 3 Buttons) und **7
`settings_ranges`** (4 Box-Numbers + 3 Burn-Lookback-Slider). Ebenfalls
verbindlich: die **Burn-Rate als OLS-Steigung** über das Lookback-Fenster, die
**D22-Diagnose-Attribute** (`burn_rate`: `lookback_minutes` / `samples` /
`lookback_too_short`; `forecast`/`pace`: `forecast_recent` / `forecast_method` /
`elapsed_fraction` / `window_seconds`) und das **echte Kalendermonat** aus
`resetsAt` statt der pauschalen 30-Tage-Näherung (§2). Der **Checker** prüft
zusätzlich `mode`, `step`, `default` (inkl. `default_required`) und
`entity_category` statisch (D16). command_gauge: ⚠️ **CG-N5** (drei
Burn-Lookback-Numbers), ⚠️ **CG-B6** (Reset-Button) und ⚠️ **CG-C3** (die
D22-Attribute) registriert — der Paar-Change steht dort noch aus.

Zusätzlich führt Kanon v1.7.0 den verbindlichen **Repository-Hygiene-/
Dokumentations-Contract** ein (`canon/repository.md`, maschinenlesbar
`canon/repository.schema.json`, Checker `scripts/check_repo_hygiene.py`). Er
regelt ausschließlich die Repository-Oberfläche: README-Paar EN/DE mit
identischem Language Switcher, My-Link, Screenshot, `hacs.json`/`manifest.json`/
Brand-Asset, Tag↔Manifest-Sync, Community-Dateien, CI-Gates und Releases. Der
**Entity-Inhalt bleibt durch den Hygiene-Contract unverändert**; go_gauge
**2.0.2** ist die Hygiene-Referenz (Checker 0 Fehler / 0 Warnungen).
command_gauge ist **⚠️ offen** (Transition: README-Paar, `render_readme`,
Community-Dateien) — Schließungsbedingung im Contract, **kein CG-Eintrag** und
kein Entity-Bruch.

Neu in v1.6.0:
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
Attribute), die **synthetische** month-Ableitung (CG-M1), **domain-begründete**
Number-Ranges sowie seit v1.7.0 die noch fehlenden command_gauge-Entities und
-Attribute (CG-N5 / CG-B6 / CG-C3).

Checker-Ergebnis: `check_canon.py` → go_gauge **0 Fehler / 0 Warnungen**
(Referenz grün), command_gauge **15 registrierte Warnungen**, **0 Fehler**. Die
D22-Diagnose-Attribute an `forecast`, `pace`, `burn_rate` sind als ⚠️ CG-C3
registriert und verschwinden mit dem ausstehenden Paar-Change in command_gauge.
