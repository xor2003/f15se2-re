#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from function_catalog import build_catalog  # noqa: E402


IDENT_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")
PTR_LINE_RE = re.compile(
    r"^(?P<name>[^/\s:]+)"
    r"(?:/(?P<var_seg>[0-9a-fA-F]+):(?P<var_off>[0-9a-fA-F]+)/(?P<linear>[0-9a-fA-F]+))?"
    r":\s+(?P<count>\d+)\s+reference(?:s)?"
    r"(?:\s+@\s+(?P<ref_seg>\w+):0x(?P<ref_off>[0-9a-fA-F]+))?$"
)
LST_DATA_RE = re.compile(
    r"^dseg:(?P<offset>[0-9A-Fa-f]{4})\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+"
    r"(?P<kind>db|dw|dd)\b"
)
RC_BSS_RE = re.compile(
    r"^(?P<name>_[A-Za-z_][A-Za-z0-9_]*)\s+.+\s+(?P<offset>[0-9A-Fa-f]+)h\s+_BSS\s+Public\b"
)
C_FUNC_START_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_\s\*]*\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*\{")


def run_capture(cmd):
    return subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)


def target_paths(target):
    if target == "start":
        return {
            "map": "map/start.map",
            "conf": "conf/start_rc.json",
            "exe": "bin/start.exe",
            "lst": "lst/start.lst",
        }
    return {
        "map": "map/egame.map",
        "conf": "conf/egame_rc.json",
        "exe": "bin/egame.exe",
        "lst": "lst/egame.lst",
    }


def find_function_entry(target, function_name):
    paths = target_paths(target)
    catalog = build_catalog(paths["map"], paths["conf"], "src")
    for item in catalog:
        if item["name"] == function_name:
            return item
    return None


def collect_identifiers(c_path):
    text = Path(c_path).read_text(encoding="utf-8", errors="replace")
    return collect_identifiers_from_text(text)


def collect_identifiers_from_text(text):
    names = set()
    for name in IDENT_RE.findall(text):
        if "_" not in name:
            continue
        if name.startswith(
            (
                "byte_",
                "word_",
                "dword_",
                "off_",
                "unk_",
                "g_",
                "stru_",
                "waypoints",
                "commData",
                "gameData",
            )
        ):
            names.add(name)
    return names


def run_mzptr(target):
    paths = target_paths(target)
    cmd = [str(ROOT / "mzretools" / "debug" / "mzptr"), paths["exe"], paths["map"]]
    result = run_capture(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "mzptr failed")
    return result.stdout


def parse_ptr_output(text):
    items = []
    for line in text.splitlines():
        match = PTR_LINE_RE.match(line.strip())
        if not match:
            continue
        items.append(
            {
                "raw_name": match.group("name"),
                "name": match.group("name"),
                "count": int(match.group("count")),
                "var_seg": int(match.group("var_seg"), 16) if match.group("var_seg") else None,
                "var_offset": int(match.group("var_off"), 16) if match.group("var_off") else None,
                "linear": int(match.group("linear"), 16) if match.group("linear") else None,
                "ref_segname": match.group("ref_seg"),
                "ref_offset": int(match.group("ref_off"), 16) if match.group("ref_off") else None,
            }
        )
    return items


def parse_lst_data_symbols(lst_path):
    symbols = []
    for raw_line in Path(lst_path).read_text(encoding="utf-8", errors="replace").splitlines():
        if match := LST_DATA_RE.match(raw_line.strip()):
            symbols.append(
                {
                    "name": match.group("name"),
                    "offset": int(match.group("offset"), 16),
                    "kind": match.group("kind"),
                }
            )
    return symbols


def parse_rc_bss_symbols(rc_lst_path):
    symbols = []
    for raw_line in Path(rc_lst_path).read_text(encoding="utf-8", errors="replace").splitlines():
        if match := RC_BSS_RE.match(raw_line.strip()):
            symbols.append(
                {
                    "name": match.group("name").lstrip("_"),
                    "offset": int(match.group("offset"), 16),
                }
            )
    return symbols


def infer_data_shift(map_offsets, symbol_offsets):
    if not map_offsets or not symbol_offsets:
        return None
    diffs = Counter()
    map_set = set(map_offsets)
    for sym_off in symbol_offsets:
        for map_off in map_set:
            delta = map_off - sym_off
            if 0 <= delta <= 0x10000:
                diffs[delta] += 1
    if not diffs:
        return None
    shift, _ = diffs.most_common(1)[0]
    return shift


def parse_map_offsets(map_path):
    map_offsets = []
    for raw_line in Path(map_path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line.startswith("var_"):
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[2] == "VAR":
            map_offsets.append(int(parts[3], 16))
    return map_offsets


def build_alias_map(map_path, lst_path, rc_lst_path):
    map_offsets = parse_map_offsets(map_path)
    aliases = defaultdict(list)
    for item in parse_lst_data_symbols(lst_path):
        aliases[item["offset"]].append(item["name"])

    rc_symbols = parse_rc_bss_symbols(rc_lst_path) if Path(rc_lst_path).exists() else []
    rc_shift = infer_data_shift(map_offsets, [item["offset"] for item in rc_symbols])
    if rc_shift is not None:
        for item in rc_symbols:
            aliases[item["offset"] + rc_shift].append(item["name"])
    return aliases, rc_shift


def unique_keep_order(items):
    out = []
    seen = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def extract_function_text(c_path, function_name):
    lines = Path(c_path).read_text(encoding="utf-8", errors="replace").splitlines()
    start = None
    brace_depth = 0
    collected = []
    for idx, raw_line in enumerate(lines):
        if start is None:
            match = C_FUNC_START_RE.match(raw_line)
            if match and match.group("name") == function_name:
                start = idx
                brace_depth = raw_line.count("{") - raw_line.count("}")
                collected.append(raw_line)
                if brace_depth <= 0:
                    return raw_line
                continue
        else:
            collected.append(raw_line)
            brace_depth += raw_line.count("{") - raw_line.count("}")
            if brace_depth <= 0:
                return "\n".join(collected)
    return Path(c_path).read_text(encoding="utf-8", errors="replace")


def build_hints(target, function_name):
    paths = target_paths(target)
    entry = find_function_entry(target, function_name)
    if not entry:
        raise RuntimeError(f"Function not found: {function_name}")
    if not entry.get("c_files"):
        raise RuntimeError(f"Function is not C-owned: {function_name}")

    c_path = entry["c_files"][0]
    c_abs = ROOT / c_path if not Path(c_path).is_absolute() else Path(c_path)
    function_text = extract_function_text(c_abs, function_name)
    identifiers = collect_identifiers_from_text(function_text)
    ptr_items = parse_ptr_output(run_mzptr(target))
    rc_lst = "egame_rc.lst" if target == "egame" else "start_rc.lst"
    aliases, rc_shift = build_alias_map(paths["map"], paths["lst"], rc_lst)

    scoped = []
    for item in ptr_items:
        alias_names = aliases.get(item["var_offset"] or -1, [])
        alias_names = unique_keep_order(alias_names)
        used = unique_keep_order([name for name in alias_names if name in identifiers])
        if item["name"] not in identifiers and not used:
            continue
        scoped.append(
            {
                **item,
                "aliases": alias_names,
                "used_in_c": used if used else ([item["name"]] if item["name"] in identifiers else []),
            }
        )

    scoped.sort(key=lambda item: (item["count"], item["name"]))
    return {
        "function": function_name,
        "segment": entry["segment"],
        "range_begin": entry["begin"],
        "range_end": entry["end"],
        "c_file": c_path,
        "identifier_count": len(identifiers),
        "rc_map_shift": rc_shift,
        "matched_hints": scoped,
    }


def main():
    parser = argparse.ArgumentParser(description="Show function-local mzptr-derived data/global hints for a C-owned function.")
    parser.add_argument("--target", choices=["egame", "start"], default="egame")
    parser.add_argument("--function", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_hints(args.target, args.function)
    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"Function: {report['function']}")
    print(f"C file: {report['c_file']}")
    print(f"Code range: {report['segment']}:{report['range_begin']:04x}-{report['range_end']:04x}")
    if report["rc_map_shift"] is not None:
        print(f"Inferred egame_rc.lst BSS-to-map shift: 0x{report['rc_map_shift']:x}")
    if not report["matched_hints"]:
        print("No mzptr hints matched globals used in this routine.")
        return

    print("mzptr hints for globals used in this routine:")
    for item in report["matched_hints"][:20]:
        alias_text = ""
        if item["aliases"]:
            alias_text = f" aliases={','.join(item['aliases'][:3])}"
        used_text = ""
        if item["used_in_c"]:
            used_text = f" used_in_c={','.join(item['used_in_c'])}"
        sample = ""
        if item["ref_segname"] and item["ref_offset"] is not None:
            sample = f" sample_ref={item['ref_segname']}:0x{item['ref_offset']:x}"
        print(
            f"- {item['name']} var_off=0x{(item['var_offset'] or 0):x} "
            f"count={item['count']}{sample}{alias_text}{used_text}"
        )


if __name__ == "__main__":
    main()
