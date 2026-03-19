#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


SEGMENT_RE = re.compile(r"^(\w+)\s+(CODE|DATA|STACK)\s+([0-9a-fA-F]+)$")
ROUTINE_RE = re.compile(r"^([\w_]+):\s+(\w+)\s+(NEAR|FAR)\s+([0-9a-fA-F]+)-([0-9a-fA-F]+)(?:\s+(.*))?$")


def strip_json_comments(text):
    return "\n".join(line for line in text.splitlines() if not re.match(r"^\s*//", line))


def load_conf(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(strip_json_comments(text))


def parse_map(path):
    segments = {}
    routines = {}
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
        match = ROUTINE_RE.match(line)
        if not match:
            continue
        segment_name = match.group(2)
        routines[match.group(1)] = {
            "name": match.group(1),
            "segment": segment_name,
            "kind": match.group(3),
            "begin": int(match.group(4), 16),
            "end": int(match.group(5), 16),
            "attrs": sorted(set((match.group(6) or "").split())),
            "image_begin": 0x10000 + (segments.get(segment_name, {}).get("base", 0) << 4) + int(match.group(4), 16),
        }
    return routines


def replace_array_in_text(text, key, items):
    pattern = re.compile(rf'("{re.escape(key)}"\s*:\s*)\[(.*?)\]', re.S)
    match = pattern.search(text)
    if not match:
        raise ValueError(f'Unable to locate array "{key}" in config text')

    indent = "    "
    rendered = []
    for item in items:
        rendered.append(indent * 2 + json.dumps(item, ensure_ascii=False))
    body = "\n"
    if rendered:
        body += ",\n".join(rendered) + "\n" + indent
    return text[: match.start(2)] + body + text[match.end(2) :]


def make_extract_entry(routine):
    return {
        "seg": routine["segment"],
        "begin": f"0x{routine['begin']:x}",
        "end": f"0x{routine['end']:x}",
        "from": routine["symbol"],
        "to": "endp",
    }


def dedupe_strings(items):
    seen = set()
    out = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def routine_aliases(routine):
    aliases = [routine["name"]]
    hex_alias = f"sub_{routine['image_begin']:X}"
    if hex_alias not in aliases:
        aliases.append(hex_alias)
    lower_alias = hex_alias.lower()
    if lower_alias not in aliases:
        aliases.append(lower_alias)
    return aliases


def choose_symbol_name(routine, conf):
    aliases = routine_aliases(routine)
    range_match = next(
        (
            item
            for item in conf.get("extract", [])
            if item.get("seg") == routine["segment"]
            and int(item.get("begin", "0"), 16) == routine["begin"]
            and int(item.get("end", "0"), 16) == routine["end"]
            and item.get("from")
        ),
        None,
    )
    if range_match:
        return range_match["from"]
    for extern_name in conf.get("externs", []):
        if extern_name in aliases:
            return extern_name
    return aliases[1] if routine["name"].startswith("routine_") and len(aliases) > 1 else routine["name"]


def remove_extracts(extracts, routine):
    aliases = set(routine_aliases(routine))
    out = []
    for item in extracts:
        same_name = item.get("from") in aliases
        same_range = (
            item.get("seg") == routine["segment"]
            and int(item.get("begin", "0"), 16) == routine["begin"]
            and int(item.get("end", "0"), 16) == routine["end"]
        )
        if same_name or same_range:
            continue
        out.append(item)
    return out


def promote(conf, routine):
    routine = dict(routine)
    routine["symbol"] = choose_symbol_name(routine, conf)
    conf["extract"] = remove_extracts(conf.get("extract", []), routine)
    conf["extract"].append(make_extract_entry(routine))
    conf["extract"].sort(key=lambda item: (item.get("seg", ""), int(item.get("begin", "0"), 16), int(item.get("end", "0"), 16)))
    conf["externs"] = dedupe_strings(conf.get("externs", []) + [routine["symbol"]])
    conf["externs"].sort()
    return conf


def demote(conf, routine):
    aliases = set(routine_aliases(routine))
    conf["extract"] = remove_extracts(conf.get("extract", []), routine)
    conf["externs"] = [item for item in conf.get("externs", []) if item not in aliases]
    return conf


def main():
    parser = argparse.ArgumentParser(description="Promote/demote a function in conf/*.json using a map file.")
    parser.add_argument("action", choices=["show", "promote", "demote"])
    parser.add_argument("--conf", required=True, help="Config path")
    parser.add_argument("--map", required=True, help="Map path")
    parser.add_argument("--function", required=True, help="Routine name")
    parser.add_argument("--write", action="store_true", help="Write changes back to config")
    args = parser.parse_args()

    conf_path = Path(args.conf)
    raw_text = conf_path.read_text(encoding="utf-8")
    conf = load_conf(conf_path)
    routines = parse_map(args.map)
    if args.function not in routines:
        raise SystemExit(f"Function not found in map: {args.function}")
    routine = routines[args.function]

    if args.action == "show":
        aliases = routine_aliases(routine)
        result = {
            "routine": routine,
            "aliases": aliases,
            "symbol": choose_symbol_name(routine, conf),
            "extract_present": any(
                item.get("from") in aliases
                or (
                    item.get("seg") == routine["segment"]
                    and int(item.get("begin", "0"), 16) == routine["begin"]
                    and int(item.get("end", "0"), 16) == routine["end"]
                )
                for item in conf.get("extract", [])
            ),
            "extern_present": any(alias in conf.get("externs", []) for alias in aliases),
        }
        print(json.dumps(result, indent=2))
        return

    if args.action == "promote":
        conf = promote(conf, routine)
    else:
        conf = demote(conf, routine)

    if args.write:
        updated = replace_array_in_text(raw_text, "extract", conf.get("extract", []))
        updated = replace_array_in_text(updated, "externs", conf.get("externs", []))
        conf_path.write_text(updated + ("" if updated.endswith("\n") else "\n"), encoding="utf-8")
        print(f"Wrote {args.action} for {args.function} to {conf_path}")
    else:
        print(json.dumps({"extract": conf.get("extract", []), "externs": conf.get("externs", [])}, indent=2))


if __name__ == "__main__":
    main()
