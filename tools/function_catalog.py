#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


SEGMENT_RE = re.compile(r"^(\w+)\s+(CODE|DATA|STACK)\s+([0-9a-fA-F]+)$")
ROUTINE_RE = re.compile(r"^([\w_]+):\s+(\w+)\s+(NEAR|FAR)\s+([0-9a-fA-F]+)-([0-9a-fA-F]+)(?:\s+(.*))?$")
C_FUNC_RE = re.compile(
    r"^\s*(?:unsigned\s+)?(?:void|char|int|long|__int\d+)\s+(?:__cdecl\s+)?(?:far\s+)?(\w+)\s*\([^;{}]*\)\s*\{",
    re.M,
)


def strip_json_comments(text):
    return "\n".join(line for line in text.splitlines() if not re.match(r"^\s*//", line))


def load_conf(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(strip_json_comments(text))


def parse_map(path):
    segments = {}
    routines = []
    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if match := SEGMENT_RE.match(line):
            segments[match.group(1)] = {
                "class": match.group(2),
                "base": int(match.group(3), 16),
            }
            continue
        if match := ROUTINE_RE.match(line):
            attrs = set((match.group(6) or "").split())
            routines.append(
                {
                    "name": match.group(1),
                    "segment": match.group(2),
                    "kind": match.group(3),
                    "begin": int(match.group(4), 16),
                    "end": int(match.group(5), 16),
                    "attrs": sorted(attrs),
                }
            )
    return segments, routines


def parse_c_functions(src_dir):
    owners = {}
    src_root = (ROOT / src_dir).resolve() if not Path(src_dir).is_absolute() else Path(src_dir).resolve()
    for path in sorted(src_root.glob("*.c")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in C_FUNC_RE.findall(text):
            owners.setdefault(name, []).append(str(path.relative_to(ROOT.resolve())))
    return owners


def index_extracts(config):
    out = {}
    for item in config.get("extract", []):
        key = (item.get("seg"), int(item.get("begin", "0"), 16), int(item.get("end", "0"), 16))
        out[key] = item
        if "from" in item:
            out[item["from"]] = item
    return out


def routine_aliases(routine):
    aliases = [routine["name"]]
    image_begin = 0x10000 + routine.get("segment_base", 0) * 0x10 + routine["begin"]
    hex_alias = f"sub_{image_begin:X}"
    if hex_alias not in aliases:
        aliases.append(hex_alias)
    lower_alias = hex_alias.lower()
    if lower_alias not in aliases:
        aliases.append(lower_alias)
    return aliases


def infer_status(routine, extract_idx, externs, preserves, c_owners):
    name = routine["name"]
    aliases = routine_aliases(routine)
    key = (routine["segment"], routine["begin"], routine["end"])
    extracted = key in extract_idx or any(alias in extract_idx for alias in aliases)
    externed = any(alias in externs for alias in aliases)
    preserved = any(alias in preserves for alias in aliases)
    has_c = any(alias in c_owners for alias in aliases)
    assembly = "assembly" in routine["attrs"]
    complete = "complete" in routine["attrs"]

    if externed and has_c:
        return "c-owned"
    if extracted and not externed:
        return "extracted-only"
    if externed and not extracted:
        return "extern-only"
    if has_c:
        return "c-present"
    if preserved or assembly:
        return "asm-preserved"
    if complete:
        return "complete-map"
    return "asm"


def build_catalog(map_path, conf_path, src_dir):
    segments, routines = parse_map(map_path)
    conf = load_conf(conf_path)
    extract_idx = index_extracts(conf)
    externs = set(conf.get("externs", []))
    preserves = set(conf.get("preserves", []))
    c_owners = parse_c_functions(src_dir)
    catalog = []
    for routine in routines:
        entry = dict(routine)
        entry["segment_base"] = segments.get(routine["segment"], {}).get("base", 0)
        aliases = routine_aliases(routine)
        entry["size"] = routine["end"] - routine["begin"] + 1
        entry["aliases"] = aliases
        entry["extracted"] = (routine["segment"], routine["begin"], routine["end"]) in extract_idx or any(alias in extract_idx for alias in aliases)
        entry["externed"] = any(alias in externs for alias in aliases)
        entry["preserved"] = any(alias in preserves for alias in aliases)
        c_files = []
        for alias in aliases:
            c_files.extend(c_owners.get(alias, []))
        entry["c_files"] = sorted(set(c_files))
        entry["status"] = infer_status(routine, extract_idx, externs, preserves, c_owners)
        catalog.append(entry)
    return catalog


def print_table(catalog):
    header = f"{'status':14} {'segment':10} {'range':15} {'name':32} {'c file'}"
    print(header)
    print("-" * len(header))
    for item in catalog:
        c_file = ",".join(item["c_files"])
        rng = f"{item['begin']:04x}-{item['end']:04x}"
        print(f"{item['status']:14} {item['segment']:10} {rng:15} {item['name']:32} {c_file}")


def main():
    parser = argparse.ArgumentParser(description="Build a function ownership catalog from map/conf/C sources.")
    parser.add_argument("--map", required=True, help="Map file, e.g. map/egame.map")
    parser.add_argument("--conf", required=True, help="Config file, e.g. conf/egame_rc.json")
    parser.add_argument("--src-dir", default="src", help="Source directory (default: %(default)s)")
    parser.add_argument("--name", help="Filter to one function name")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    catalog = build_catalog(args.map, args.conf, args.src_dir)
    if args.name:
        catalog = [item for item in catalog if item["name"] == args.name]

    if args.json:
        print(json.dumps(catalog, indent=2))
    else:
        print_table(catalog)


if __name__ == "__main__":
    main()
