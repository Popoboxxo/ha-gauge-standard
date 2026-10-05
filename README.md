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
| **Master/Stil-Referenz** | [`ha-go-gauge`](https://github.com/Popoboxxo/ha-go-gauge) — wo sich Integrationen unterscheiden, gilt `go_gauge` **1.6.0** als Kanon-Entscheidung, sofern unten nicht anders festgelegt. |
| **Consumer** | [`ha-go-gauge`](https://github.com/Popoboxxo/ha-go-gauge) (`go_gauge`) und [`ha-command-gauge`](https://github.com/Popoboxxo/ha-command-gauge) (`command_gauge`). `command_gauge` ist das aktive **Konvergenz-Ziel**. |
| **Paar-Change-Pflicht** | Jede Kanon-Änderung ist ein **Paar-Change**: sie wird in beiden Integrationen umgesetzt (soweit die jeweilige API hergibt) — nie nur in einem Repo. |
| **Ausnahmen** | Domain-begründete Divergenz ist nur mit ⚠️-Eintrag im Kanon erlaubt, inkl. Begründung und **Schließungsbedingung** (*closing condition*). |

## Inhalt

```
canon/
  entities.md          # verbindlicher Kanon v1.1 (menschenlesbar, Deutsch)
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

Kanon **v1.1** — abgeleitet aus `go_gauge` 1.6.0 (Master) und
`command_gauge` 0.2.0 (Konvergenz-Ziel), Stand 2026-10-05. Neu in v1.1:
Scope-Status-Sensor `api_status` (go_gauge 1.6.0) und `subscription_active`
ohne device_class.
