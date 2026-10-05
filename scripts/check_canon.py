#!/usr/bin/env python3
"""Check a Gauge integration (custom_components/<domain>) against the canon.

Reads the platform files sensor/binary_sensor/number/switch/button (.py),
strings.json and translations/{en,de}.json of an integration repository and
verifies them against canon/entities.schema.json:

  - translation_keys of all canon entities present (canon key or registered
    per-domain alias)
  - translation completeness (code key exists in strings.json + en.json + de.json)
  - attribute names of extra_state_attributes present
  - icon / unit / device_class / state_class consistency
  - unique_id suffix token consistency
  - settings_ranges (min/max of the four Number entities)
  - window set (WINDOW_LABELS in const.py)
  - no hardcoded _attr_name literals

Deviations registered in the schema's known_deviations for the detected
domain are reported as WARNING (exit stays 0); anything else is an ERROR
(exit 1). Usage:

    python scripts/check_canon.py <repo-root> [--domain go_gauge|command_gauge]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLATFORMS = ("sensor", "binary_sensor", "number", "switch", "button")
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = SCRIPT_DIR.parent / "canon" / "entities.schema.json"

CLASS_BLOCK_RE = re.compile(r"^(class\s+\w+\([^)]*\):.*?)(?=^class\s|\Z)", re.M | re.S)
CLASS_HEADER_RE = re.compile(r"^class\s+(\w+)\(([^)]*)\)")


class ClassInfo:
    """Statically extracted facts about one entity class."""

    def __init__(self, name: str, body: str, consts: dict[str, str]) -> None:
        self.name = name
        self.body = body
        self.consts = consts
        m = re.search(r'_attr_translation_key\s*=\s*"([^"]+)"', body)
        self.translation_key = m.group(1) if m else None
        self.icons = set(re.findall(r"mdi:[a-z0-9-]+", body))
        m = re.search(r'_attr_native_unit_of_measurement\s*=\s*"([^"]+)"', body)
        self.unit = m.group(1) if m else None
        m = re.search(r"_attr_device_class\s*=\s*\w+DeviceClass\.(\w+)", body)
        self.device_class = m.group(1) if m else None
        m = re.search(r"_attr_state_class\s*=\s*\w+StateClass\.(\w+)", body)
        self.state_class = m.group(1) if m else None
        self.bases = self._extract_bases()
        self.attributes = self._extract_attributes()
        self.min_value = self._int_or_none(
            r"(?:min_value|_minimum)\s*=\s*(\d+)")
        self.max_value = self._int_or_none(
            r"(?:max_value|_maximum)\s*=\s*(\d+)")
        self.unique_suffix = self._resolve_suffix()

    def _literal_token(self, template: str) -> str | None:
        parts = [p for p in re.split(r"\{[^}]*\}", template) if p.strip("_")]
        if not parts:
            return None
        token = parts[-1].strip("_")
        return token or None

    def _own_suffix(self) -> str | None:
        m = re.search(r'_attr_unique_id\s*=\s*f?"([^"]+)"', self.body)
        if m:
            token = self._literal_token(m.group(1))
            if token:
                return token
        m = re.search(r'unique_suffix\s*=\s*"([^"]+)"', self.body)
        if m:
            return m.group(1)
        m = re.search(r'_option\s*=\s*"([^"]+)"', self.body)
        if m:
            return m.group(1)
        m = re.search(r"_option\s*=\s*([A-Z][A-Z0-9_]*)", self.body)
        if m:
            return self.consts.get(m.group(1))
        return None

    def _resolve_suffix(self) -> str | None:
        return self._own_suffix()

    def _extract_attributes(self) -> set[str]:
        m = re.search(r"def extra_state_attributes\b", self.body)
        if not m:
            return set()
        start = m.end()
        nxt = re.search(r"\n    def \w+\(", self.body[start:])
        segment = self.body[start:start + nxt.start()] if nxt else self.body[start:]
        keys = set(re.findall(r'"([a-zA-Z0-9_]+)"\s*:', segment))
        keys |= set(re.findall(r'\["([a-zA-Z0-9_]+)"\]', segment))
        return keys

    def _extract_bases(self) -> list[str]:
        m = CLASS_HEADER_RE.match(self.body)
        if not m:
            return []
        return [b.strip().split(".")[-1] for b in m.group(2).split(",") if b.strip()]

    def _int_or_none(self, pattern: str) -> int | None:
        m = re.search(pattern, self.body)
        return int(m.group(1)) if m else None


def parse_classes(source: str, consts: dict[str, str]) -> dict[str, ClassInfo]:
    classes: dict[str, ClassInfo] = {}
    for block in CLASS_BLOCK_RE.finditer(source):
        header = CLASS_HEADER_RE.match(block.group(1))
        if header:
            classes[header.group(1)] = ClassInfo(header.group(1), block.group(1), consts)
    return classes


def parse_consts(source: str) -> dict[str, str]:
    """Literal string constants (CONF_* = \"...\") resolvable for _option refs."""
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r'^([A-Z][A-Z0-9_]*)\s*=\s*"([^"]+)"', source, re.M)
    }


def resolve_range(info: ClassInfo, classes: dict[str, ClassInfo],
                  attr: str, seen: set[str] | None = None) -> int | None:
    """Own min/max or inherited from the first known base class."""
    seen = seen or set()
    value = getattr(info, attr)
    if value is not None or info.name in seen:
        return value
    seen.add(info.name)
    for base in info.bases:
        if base in classes:
            found = resolve_range(classes[base], classes, attr, seen)
            if found is not None:
                return found
    return None


def resolve_icons(info: ClassInfo, classes: dict[str, ClassInfo],
                  seen: set[str] | None = None) -> set[str]:
    """Own icons merged with all base-class icons (recursively)."""
    seen = seen or set()
    if info.name in seen:
        return set()
    seen.add(info.name)
    icons = set(info.icons)
    for base in info.bases:
        if base in classes:
            icons |= resolve_icons(classes[base], classes, seen)
    return icons


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as err:
        print(f"ERROR: {path}: invalid JSON: {err}")
        return {}


def entity_name(translations: dict, platform: str, key: str) -> str | None:
    node = translations.get("entity", {}).get(platform, {}).get(key, {})
    return node.get("name")


def detect_domain(repo: Path, schema: dict, forced: str | None) -> str | None:
    known = {schema["master"]["domain"], schema["convergence_target"]["domain"]}
    if forced:
        return forced
    components = repo / "custom_components"
    if not components.is_dir():
        return None
    for manifest in sorted(components.glob("*/manifest.json")):
        try:
            domain = json.loads(manifest.read_text(encoding="utf-8")).get("domain")
        except (json.JSONDecodeError, OSError):
            continue
        if domain in known:
            return domain
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path, help="integration repo root")
    parser.add_argument("--domain", choices=("go_gauge", "command_gauge"))
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    repo: Path = args.repo
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    domain = detect_domain(repo, schema, args.domain)
    if domain is None:
        print(f"ERROR: cannot detect domain in {repo}/custom_components "
              f"(use --domain)")
        return 1

    components = repo / "custom_components" / domain
    if not components.is_dir():
        print(f"ERROR: {components} not found")
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    def report(entity_id: str, aspect: str, detail: str) -> None:
        entry = (entity_id, aspect)
        if entry in deviations:
            dev = deviations[entry]
            warnings.append(
                f"⚠️  [{entity_id}/{aspect}] {detail}\n"
                f"    registered deviation: {dev['reason']}\n"
                f"    closing condition: {dev['closing']}")
        else:
            errors.append(f"[{entity_id}/{aspect}] {detail}")

    deviations = {
        (d["id"], d["aspect"]): d
        for d in schema.get("known_deviations", {}).get(domain, [])
    }

    # --- parse platform sources -------------------------------------------
    const_py = components / "const.py"
    consts = parse_consts(const_py.read_text(encoding="utf-8")) if const_py.is_file() else {}

    platform_sources: dict[str, str] = {}
    classes_by_platform: dict[str, dict[str, ClassInfo]] = {}
    for platform in PLATFORMS:
        path = components / f"{platform}.py"
        if not path.is_file():
            errors.append(f"[files] missing platform file: {path}")
            continue
        source = path.read_text(encoding="utf-8")
        platform_sources[platform] = source
        classes_by_platform[platform] = parse_classes(source, consts)

    # entity.py: no hardcoded _attr_name literals (canon naming rule)
    entity_py = components / "entity.py"
    if entity_py.is_file():
        platform_sources["entity.py"] = entity_py.read_text(encoding="utf-8")
    for name, source in platform_sources.items():
        if re.search(r"^\s*_attr_name\s*=", source, re.M):
            errors.append(f"[naming] hardcoded _attr_name literal in {name}")

    # --- translations ------------------------------------------------------
    translations: dict[str, dict] = {}
    for rel in schema["naming"]["translation_files"]:
        translations[rel] = load_json(components / rel)

    # --- canon entities ----------------------------------------------------
    key_to_class: dict[tuple[str, str], ClassInfo] = {}
    code_keys: dict[str, set[str]] = {p: set() for p in PLATFORMS}
    for platform, classes in classes_by_platform.items():
        for info in classes.values():
            if info.translation_key:
                code_keys[platform].add(info.translation_key)
                key_to_class[(platform, info.translation_key)] = info

    aliases = schema["master"].get("aliases", {})
    extensions = {
        ext["translation_key"]
        for ext in schema.get("domain_extensions", {}).get(domain, [])
    }

    for entity in schema["entities"]:
        eid = entity["id"]
        platform = entity["platform"]
        canon_key = entity["translation_key"]
        wanted = canon_key
        if domain != schema["master"]["domain"]:
            wanted = entity.get("aliases", {}).get(domain, canon_key)
        info = key_to_class.get((platform, wanted))

        if info is None:
            report(eid, "presence",
                   f"entity not found (canon key '{canon_key}'"
                   + (f", alias '{wanted}')" if wanted != canon_key else ")"))
            continue

        if info.translation_key != canon_key:
            report(eid, "translation_key",
                   f"uses '{info.translation_key}' instead of canon key "
                   f"'{canon_key}'")

        en_name = entity_name(translations["translations/en.json"],
                              platform, info.translation_key)
        for rel in schema["naming"]["translation_files"]:
            name = entity_name(translations[rel], platform, info.translation_key)
            if name is None:
                errors.append(
                    f"[{eid}/translations] '{info.translation_key}' missing in "
                    f"{rel} (entity.{platform})")
        if en_name is not None and "name_en" in entity:
            if en_name != entity["name_en"]:
                report(eid, "name_pattern",
                       f"en name '{en_name}' != canon '{entity['name_en']}'")

        if "unit" in entity and entity["unit"] is not None:
            if info.unit != entity["unit"]:
                report(eid, "unit",
                       f"unit '{info.unit}' != canon '{entity['unit']}'")
        if entity.get("device_class") and info.device_class != entity["device_class"]:
            report(eid, "device_class",
                   f"device_class '{info.device_class}' != canon "
                   f"'{entity['device_class']}'")
        if entity.get("state_class") and info.state_class != entity["state_class"]:
            report(eid, "state_class",
                   f"state_class '{info.state_class}' != canon "
                   f"'{entity['state_class']}'")
        if entity.get("icons"):
            actual_icons = resolve_icons(info, classes_by_platform.get(platform, {}))
            missing = set(entity["icons"]) - actual_icons
            if missing:
                report(eid, "icons",
                       f"icons missing in class {info.name}: "
                       f"{sorted(missing)}")
        if entity.get("unique_id_suffix"):
            if info.unique_suffix != entity["unique_id_suffix"]:
                report(eid, "unique_id_suffix",
                       f"suffix '{info.unique_suffix}' != canon "
                       f"'{entity['unique_id_suffix']}'")
        missing_attrs = set(entity.get("attributes", [])) - info.attributes
        if missing_attrs:
            report(eid, "attributes",
                   f"extra_state_attributes missing: {sorted(missing_attrs)}")

    # --- settings ranges (numbers) ----------------------------------------
    for key, spec in schema.get("settings_ranges", {}).items():
        canon_key = spec["number"]
        wanted = canon_key
        if domain != schema["master"]["domain"]:
            wanted = next(
                (e.get("aliases", {}).get(domain, canon_key)
                 for e in schema["entities"] if e["id"] == key), canon_key)
        info = key_to_class.get(("number", wanted))
        if info is None:
            continue  # presence already reported above
        classes = classes_by_platform.get("number", {})
        actual_min = resolve_range(info, classes, "min_value")
        actual_max = resolve_range(info, classes, "max_value")
        if actual_min != spec["min"] or actual_max != spec["max"]:
            report(key, "settings_range",
                   f"range {actual_min}..{actual_max} != canon "
                   f"{spec['min']}..{spec['max']}")

    # --- windows ------------------------------------------------------------
    if const_py.is_file():
        source = const_py.read_text(encoding="utf-8")
        m = re.search(r"WINDOW_LABELS\s*=\s*\{([^}]*)\}", source)
        actual_windows = re.findall(r'"(\w+)"\s*:', m.group(1)) if m else []
        canon_windows = schema["windows"]["order"]
        if actual_windows != canon_windows:
            report("windows", "windows",
                   f"WINDOW_LABELS {actual_windows} != canon {canon_windows}")

    # --- unknown translation keys (unregistered divergence) ---------------
    canon_keys = {e["translation_key"] for e in schema["entities"]}
    for platform, keys in code_keys.items():
        for key in sorted(keys):
            known = key in canon_keys or key in extensions
            if not known and domain != schema["master"]["domain"]:
                known = any(e.get("aliases", {}).get(domain) == key
                            for e in schema["entities"])
            if not known:
                errors.append(
                    f"[{platform}] translation_key '{key}' is not in the canon "
                    f"(nor an alias/domain extension)")

    # --- summary -------------------------------------------------------------
    master = schema["master"]
    role = "MASTER" if domain == master["domain"] else "CONVERGENCE TARGET"
    print(f"check_canon v{schema['canon_version']} — {domain} ({role}) @ {repo}")
    print(f"canon master: {master['domain']} {master['version']}")
    for line in warnings:
        print(f"WARN {line}")
    for line in errors:
        print(f"ERROR {line}")
    print(f"result: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
