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
    routines = {}
    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or SEGMENT_RE.match(line):
            continue
        match = ROUTINE_RE.match(line)
        if not match:
            continue
        routines[match.group(1)] = {
            "name": match.group(1),
            "segment": match.group(2),
            "kind": match.group(3),
            "begin": int(match.group(4), 16),
            "end": int(match.group(5), 16),
            "attrs": sorted(set((match.group(6) or "").split())),
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
        "from": routine["name"],
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


def remove_extracts(extracts, routine):
    out = []
    for item in extracts:
        same_name = item.get("from") == routine["name"]
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
    conf["extract"] = remove_extracts(conf.get("extract", []), routine)
    conf["extract"].append(make_extract_entry(routine))
    conf["extract"].sort(key=lambda item: (item.get("seg", ""), int(item.get("begin", "0"), 16), int(item.get("end", "0"), 16)))
    conf["externs"] = dedupe_strings(conf.get("externs", []) + [routine["name"]])
    conf["externs"].sort()
    return conf


def demote(conf, routine):
    conf["extract"] = remove_extracts(conf.get("extract", []), routine)
    conf["externs"] = [item for item in conf.get("externs", []) if item != routine["name"]]
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
        result = {
            "routine": routine,
            "extract_present": any(
                item.get("from") == routine["name"]
                or (
                    item.get("seg") == routine["segment"]
                    and int(item.get("begin", "0"), 16) == routine["begin"]
                    and int(item.get("end", "0"), 16) == routine["end"]
                )
                for item in conf.get("extract", [])
            ),
            "extern_present": routine["name"] in conf.get("externs", []),
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
