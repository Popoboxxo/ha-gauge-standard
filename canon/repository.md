# Gauge Repository-Hygiene v1.7.0

Verbindlicher Hygiene- und Dokumentations-Contract für alle Gauge-Integrationen
(`go_gauge`, `command_gauge`). Er gilt **zusätzlich** zum Entity-Kanon
(`canon/entities.md`) und ändert **keine** Entity, `unique_id`, Übersetzung oder
Options-Semantik — er regelt ausschließlich die Repository-Oberfläche, die ein
HACS-Nutzer **vor** dem ersten Start der Integration sieht.

> Interne Doku, daher Deutsch; fachliche Schlüsselbegriffe und alle
> Schema-Schlüssel bleiben Englisch (*custom repository*, *My-Link*,
> *workflow_dispatch*, …).

## 1. Geltungsbereich

Der Contract gilt für beide Distributionswege:

1. **Custom Repository** (heute der einzige Weg für die Gauge-Familie): Nutzer
   fügen das GitHub-Repo in HACS als *Custom repository* hinzu.
2. **Katalog / Store** (optional, siehe §9): sobald eine Integration in einen
   HACS-Katalog aufgenommen ist, gelten dieselben Datei- und Dokumentations-
   Pflichten unverändert weiter.

Der Contract prüft **Dateien und Metadaten im Repository**, nie
GitHub-Einstellungen (Description, Topics, Issues-Schalter). Diese werden hier
als Pflicht beschrieben, sind aber nicht maschinell prüfbar.

## 2. Öffentliches Repository

- Öffentliches GitHub-Repository unter einer stabilen Owner-URL.
- **Description** und **Topics** gesetzt (`home-assistant`, `hacs`,
  `integration` plus produktspezifische Begriffe).
- **Issues aktiviert** (Issue-Templates, §6) — der Support-Kanal ist Teil des
  Produkts.
- **OSI-Lizenz** vorhanden (`LICENSE` im Repo-Root); die README verlinkt sie.

## 3. README-Paar (English + Deutsch)

- `README.md` ist das **englische Primärdokument** (GitHub/HACS rendern es
  standardmäßig), `README.de.md` die vollständige deutsche Fassung.
- **Zeile 1 beider Dateien ist identisch** und enthält den Language Switcher:

  ```markdown
  [English](README.md) | [Deutsch](README.de.md)
  ```

- Beide READMEs sind vollständig (kein Platzhalter, englische Fassung
  > 5000 Bytes) und tragen denselben Informationsgehalt.
- Pflichtabschnitte (deutsche Entsprechungen sind zulässig):

  | Abschnitt (EN) | Deutsch (zulässig) |
  |---|---|
  | Installation | Installation |
  | Setup | Einrichtung |
  | Troubleshooting / FAQ | Troubleshooting / FAQ |
  | Diagnostics & debug logging | Diagnose & Debug-Logging |
  | Support | Support |
  | Contributing | Mitwirken |
  | Security | Sicherheit |
  | License | Lizenz |
  | Entity names and entity IDs | Entitätsnamen und Entity-IDs |

  Zusätzlich erwartet: Features, Compatibility (HA-Mindestversion, HACS-
  Generation), Entities, Migration/Upgrade, Dashboards (siehe §8).
- **Screenshot** liegt unter `docs/images/` (echtes PNG, kein Platzhalter) und
  wird aus `README.md` **und** `README.de.md` per relativem Pfad eingebettet.
- `README.md` enthält einen **Custom-Repository-Hinweis** (Suchbegriff
  `custom repository`), damit klar ist, warum die Integration nicht im
  Default-Store erscheint.
- Beide READMEs enthalten eine **Entity-Namen-/Entity-ID-Policy**
  (Pflichtabschnitt `Entity names and entity IDs` bzw. `Entitätsnamen und
  Entity-IDs`): kanonische Namen, Translation-Keys und `unique_id`s sind
  englisch; die `entity_id` erzeugt Home Assistant einmalig aus dem
  lokalisierten Anzeigenamen plus Gerätenamen und lässt sie danach stabil.
  Beispiel-Slugs im README sind Beispiele (keine Automatisierungs-Garantie),
  ein manuelles Rename ist nicht Teil des Contracts, user-defined
  Workspace-Präfixe sind zulässig. Details: `canon/entities.md` §9.1.

## 4. Installation und Distribution

- **My-Link** (Ein-Klick-Installation) in beiden READMEs:

  ```text
  https://my.home-assistant.io/redirect/hacs_repository/?owner=<owner>&repository=<repo>&category=integration
  ```

  Dazu das passende Badge (`https://my.home-assistant.io/badges/hacs_repository.svg`).
  Der Parameter `hacs_repository` ist heute verbindlich; das künftige
  Äquivalent `marketplace_repository` ist als **Zukunfts-/Alternativ-Parameter**
  vorgesehen und ersetzt `hacs_repository` erst, wenn die HACS-Generation ihn
  flächendeckend unterstützt. Der Checker akzeptiert beide Ziele, verlangt aber
  eine **vollständige Redirect-URL**: `owner=`, `repository=` und
  `category=integration` müssen im selben Link stehen — ein bloßes Badge oder
  ein einzelner Token genügt nicht.
- **Manueller Fallback** ist dokumentiert: HACS → Integrations → ⋮ →
  *Custom repositories*, URL + Kategorie `Integration`, installieren, HA neu
  starten; alternativ Kopie von `custom_components/<domain>` nach
  `/config/custom_components/<domain>`.
- Die Installation darf **keine** zusätzliche externe Komponente außer HACS
  voraussetzen.

## 5. Metadaten

### `hacs.json` (Repo-Root)

- Pflicht: `name`, `homeassistant` (unterstützte HA-Mindestversion).
- **Verboten: `render_readme`.** Der Schlüssel ist ein HACS-1.x-Überbleibsel
  ohne Wirkung und wird nicht mehr gepflegt — der Checker meldet ihn als
  **Fehler**.
- `zip_release`, `hide_default_branch` und ähnliche Legacy-Schalter nur, wenn
  der Release-Prozess sie tatsächlich braucht. Solche Schlüssel sind nicht
  verboten, aber begründungspflichtig: der Checker meldet sie als
  **WARNING** („legacy/optional hacs.json key present — must be justified“)
  und blockiert den Lauf damit nicht.

### `manifest.json` (`custom_components/<domain>/`)

Pflichtschlüssel: `domain`, `name`, `version`, `documentation`,
`issue_tracker`, `codeowners`, `config_flow`, `integration_type`, `iot_class`.

- `domain` == Verzeichnisname unter `custom_components/`.
- `version` ist **bare SemVer ohne `v`** und entspricht dem letzten Git-Tag
  (`v2.0.2` ↔ `"version": "2.0.2"`).
- `categories` ist **optional**: nur führen, sobald das ausgelieferte
  hassfest den Schlüssel akzeptiert (hassfest 2026.10 lehnt ihn mit
  `not a valid option at 'categories'` ab; die HACS-Action warnt nur, dass
  keine Kategorien gesetzt sind — diese Warnung ist **nicht blockierend**).
  Ist der Schlüssel gesetzt: Liste mit 1–3 eindeutigen, nicht-leeren Strings.

### Brand-Assets

- `custom_components/<domain>/brand/icon.png`: echtes PNG (Magic Bytes),
  **exakt 256×256** Pixel (IHDR, ohne Pillow prüfbar).
- Optional zusätzlich `logo.png`; fehlt das Icon, zeigt HACS einen Platzhalter.

## 6. Community-Dateien

| Datei | Zweck |
|---|---|
| `.github/ISSUE_TEMPLATE/bug_report.yml` | Bug-Formular (Diagnostics, Logs, HA-Version) |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | Feature-Formular |
| `.github/ISSUE_TEMPLATE/config.yml` | Issue-Chooser (`blank_issues_enabled`, `contact_links`) |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR-Checkliste (Tests, Doku, Kanon) |
| `CONTRIBUTING.md` | Setup, Testlauf, Commit-Konventionen |
| `SECURITY.md` | Meldeweg für Schwachstellen, unterstützte Versionen |
| `CODE_OF_CONDUCT.md` | Verhaltenskodex |
| `.github/CODEOWNERS` | mindestens eine `@handle`-Regel |
| `.github/dependabot.yml` | `version: 2` + `package-ecosystem` (mind. `github-actions`) |

Leere Platzhalter gelten als fehlend: jede Datei muss echten Inhalt tragen.

## 7. CI-Gates

Die Workflow-Datei `.github/workflows/validate.yml` **muss** mindestens führen:

- **HACS Action** (`hacs/action`) und **hassfest** (`hassfest`),
- Tests (`pytest`),
- Lint (`ruff`),
- Type-Check (`mypy`),
- JSON-Metadaten-Konsistenz (`check_json_consistency`),
- Gauge-Entity-Kanon (`check_canon`).

Diese Tool-Tokens sind **verbindlich**: fehlt einer, meldet der Checker einen
**Fehler** (Exit 1). Geprüft wird per Substring-Match (case-sensitiv, exakt die
Schreibweise der Referenz-Workflow-Datei).

Zusätzlich:

- Trigger `schedule` (Cron, Drift gegen bewegte Upstream-Actions) **und**
  `workflow_dispatch` (manueller Lauf).
- **Keine `ignore:`-Schlüssel** — ein stillgelegtes Gate ist schlechter als ein
  rotes Gate (Fehler).

Die Trigger sind **empfohlen, aber nicht blockierend**: der Checker meldet
einen fehlenden `schedule:`-/`workflow_dispatch:`-Trigger als **WARNING**
(Exit bleibt 0), die Tool-Tokens dagegen als **Fehler**.

## 8. Releases und Versionierung

- **SemVer**: MAJOR = Breaking, MINOR = Feature, PATCH = Fix. Entity-/
  `unique_id`-Änderungen sind **immer** MAJOR.
- Tag-Format Stable `vMAJOR.MINOR.PATCH`, Beta `vX.Y.ZbN` (GitHub-Release als
  *pre-release* markiert).
- **Voller GitHub-Release**, nicht nur ein Tag: HACS verteilt ausschließlich
  echte Releases.
- **Tag ↔ `manifest.version`** synchron (Tag ohne `v` == Manifest-Version).
  Lässt sich in einer flachen CI-Kopie kein Tag ermitteln, ist das ein
  **Warnfall**, kein Fehler — der Checker meldet dann
  „Tag-Info nicht verfügbar“.
- Release Notes mit Summary, Features, Breaking Changes (inkl.
  Migrationshinweis) und `CHANGELOG.md`-Block. `CHANGELOG.md` enthält eine
  Versionsüberschrift `## [<version>]` zur Manifest-Version.

## 9. Katalog (optional)

- Ein Eintrag im HACS-Default-Katalog/Store ist **optional** und nicht Teil
  dieses Contracts.
- Das **Custom Repository über den My-Link ist ausdrücklich unterstützt** und
  bleibt der primäre Weg; der Contract gilt für beide Distributionspfade
  identisch.
- Keine README-Aussage darf eine Default-Store-Verfügbarkeit behaupten, solange
  die Integration dort nicht gelistet ist (Negation ist Pflicht).

## 10. Verifikation

```bash
# Referenz (go_gauge): muss grün sein, Exit 0
python3 scripts/check_repo_hygiene.py /pfad/zu/ha-go-gauge

# Konvergenz-Ziel (command_gauge): Lücken als WARNING, Exit 0
python3 scripts/check_repo_hygiene.py /pfad/zu/ha-command-gauge --warn-only
```

Exit-Codes: `0` = keine Fehler (im `--warn-only`-Modus werden alle Findings zu
Warnungen), `1` = mindestens ein Fehler bzw. unlesbarer Repo-Pfad. Der Checker
arbeitet **nur auf Dateien**, nutzt die Python-Standardbibliothek und ist
HA-frei. `canon/repository.schema.json` beschreibt diesen Contract
maschinenlesbar; **ausführbarer Regelsatz ist der Checker**
(`scripts/check_repo_hygiene.py`). Nicht jeder Schema-Schlüssel wird 1:1 vom
Code konsumiert (GitHub-Einstellungen wie Description/Topics lassen sich aus
einem Checkout nicht prüfen) — bei Abweichungen gilt der Checker. `--schema
PATH` erlaubt eine abweichende Schema-Datei.

## 11. Ausnahmen und Transition

| Integration | Stand | Bemerkung |
|---|---|---|
| `go_gauge` | ✅ erfüllt | Referenz (2.0.2): README-Paar, My-Link, Screenshot, Community-Dateien, CI-Gates, Tag-Sync. |
| `command_gauge` | ⚠️ offen / Transition | Historisch gewachsen (nur `README.md`, `render_readme` in `hacs.json`, keine Community-Dateien). |

**Schließungsbedingung für `command_gauge`:** „Hygiene-Contract umgesetzt
(README EN/DE, Templates, Community-Dateien, Checker grün)“.

Die Transition ist **keine Entity-Abweichung**: kein Entity-Bruch, keine
`unique_id`-Änderung und deshalb **kein neuer CG-Eintrag**. Bis zur Schließung
läuft der Checker für `command_gauge` mit `--warn-only` (CI bleibt grün, die
Lücken bleiben sichtbar).

## 12. Checkliste vor dem Release

- [ ] `README.md` + `README.de.md`, Zeile 1 identisch, My-Link + Badge.
- [ ] Screenshot unter `docs/images/`, aus beiden READMEs eingebettet.
- [ ] `hacs.json` ohne `render_readme`; `manifest.json` vollständig.
- [ ] `brand/icon.png` 256×256; Tag ↔ Manifest synchron.
- [ ] Issue-/PR-Templates, CONTRIBUTING, SECURITY, CoC, CODEOWNERS, Dependabot.
- [ ] CI: HACS + hassfest + Tests + Lint + mypy + JSON + Kanon, `schedule` +
      `workflow_dispatch`, kein `ignore:`.
- [ ] GitHub-Release mit Notes; `CHANGELOG.md`-Block vorhanden.
- [ ] `python3 scripts/check_repo_hygiene.py <repo>` → Exit 0.
