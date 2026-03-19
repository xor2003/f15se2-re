#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


C_FUNC_DEF_RE = re.compile(
    r"^\s*(?:static\s+)?(?:unsigned\s+)?(?:void|char|int|long|__int\d+)\s+"
    r"(?:__cdecl\s+)?(?:far\s+)?(\w+)\s*\([^;{}]*\)\s*\{?\s*$",
    re.I,
)
ASM_PROC_RE = re.compile(r"^\s*_?(\w+)\s+PROC\b", re.I)
ASM_ENDP_RE = re.compile(r"^\s*_?(\w+)\s+ENDP\b", re.I)
ASM_CALL_RE = re.compile(r"\bcall\b(?:\s+far\s+ptr)?\s+([A-Za-z_]\w*)", re.I)
ASM_JUMP_RE = re.compile(r"\bjmp\b(?:\s+short|\s+far\s+ptr)?\s+([A-Za-z_]\w*)", re.I)
LOCAL_LABEL_RE = re.compile(r"^(?:loc|short|sub)_[0-9A-Fa-f]+$", re.I)
MAP_ROUTINE_RE = re.compile(r"^([\w_]+):\s+(\w+)\s+(NEAR|FAR)\s+([0-9a-fA-F]+)-([0-9a-fA-F]+)(?:\s+(.*))?$")
LST_LINE_RE = re.compile(r"^(\w+):([0-9a-fA-F]{4})\s+(.*)$")


def read_lines(path):
    return path.read_text(encoding="cp437", errors="replace").splitlines()


def iter_source_files(donor_dir):
    root = Path(donor_dir)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".c", ".h", ".asm", ".inc"}:
            continue
        yield path


def relative_string(path, donor_dir):
    return str(path.relative_to(Path(donor_dir)))


def extract_c_definition(path, function_name):
    lines = read_lines(path)
    for index, line in enumerate(lines):
        match = C_FUNC_DEF_RE.match(line)
        if not match or match.group(1) != function_name:
            continue

        snippet = [line]
        depth = line.count("{") - line.count("}")
        saw_open = "{" in line
        end_index = index

        for cursor in range(index + 1, len(lines)):
            snippet.append(lines[cursor])
            if "{" in lines[cursor]:
                saw_open = True
            depth += lines[cursor].count("{") - lines[cursor].count("}")
            end_index = cursor
            if saw_open and depth <= 0:
                break

        return {
            "kind": "c-definition",
            "path": str(path),
            "relative_path": None,
            "start_line": index + 1,
            "end_line": end_index + 1,
            "snippet": "\n".join(snippet).strip() + "\n",
        }
    return None


def extract_asm_proc(path, function_name):
    lines = read_lines(path)
    start_index = None
    for index, line in enumerate(lines):
        match = ASM_PROC_RE.match(line)
        if match and match.group(1) == function_name:
            start_index = index
            break
    if start_index is None:
        return None

    end_index = start_index
    for index in range(start_index + 1, len(lines)):
        match = ASM_ENDP_RE.match(lines[index])
        if match and match.group(1) == function_name:
            end_index = index
            break

    return {
        "kind": "asm-proc",
        "path": str(path),
        "relative_path": None,
        "start_line": start_index + 1,
        "end_line": end_index + 1,
        "snippet": "\n".join(lines[start_index : end_index + 1]).strip() + "\n",
    }


def extract_asm_function_text(path, function_name):
    proc = extract_asm_proc(path, function_name)
    if not proc:
        return None
    return proc["snippet"]


def parse_map_routine(path, function_name):
    for raw_line in read_lines(Path(path)):
        line = raw_line.strip()
        match = MAP_ROUTINE_RE.match(line)
        if not match or match.group(1) != function_name:
            continue
        return {
            "segment": match.group(2),
            "begin": int(match.group(4), 16),
            "end": int(match.group(5), 16),
        }
    return None


def extract_asm_function_from_lst(lst_path, map_path, function_name):
    routine = parse_map_routine(map_path, function_name)
    if not routine:
        return None
    lines = []
    for raw_line in read_lines(Path(lst_path)):
        match = LST_LINE_RE.match(raw_line)
        if not match:
            continue
        segment = match.group(1)
        offset = int(match.group(2), 16)
        if segment != routine["segment"]:
            continue
        if offset < routine["begin"] or offset > routine["end"]:
            continue
        lines.append(raw_line.rstrip())
    if not lines:
        return None
    return "\n".join(lines).strip() + "\n"


def extract_called_symbols_from_asm_text(asm_text):
    symbols = []
    seen = set()
    for line in asm_text.splitlines():
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        match = ASM_CALL_RE.search(code) or ASM_JUMP_RE.search(code)
        if not match:
            continue
        symbol = match.group(1).lstrip("_")
        if LOCAL_LABEL_RE.match(symbol):
            continue
        if symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)
    return symbols


def find_references(path, function_name, max_refs):
    pattern = re.compile(rf"\b_?{re.escape(function_name)}\b")
    hits = []
    for index, line in enumerate(read_lines(path), start=1):
        if not pattern.search(line):
            continue
        hits.append(
            {
                "path": str(path),
                "relative_path": None,
                "line": index,
                "text": line.rstrip(),
            }
        )
        if len(hits) >= max_refs:
            break
    return hits


def build_donor_report(function_name, donor_dir, max_refs=8):
    donor_root = Path(donor_dir)
    report = {
        "function": function_name,
        "donor_dir": str(donor_root),
        "exact_matches": [],
        "reference_hits": [],
    }

    ref_budget = max_refs
    for path in iter_source_files(donor_root):
        exact = None
        if path.suffix.lower() in {".c", ".h"}:
            exact = extract_c_definition(path, function_name)
        elif path.suffix.lower() in {".asm", ".inc"}:
            exact = extract_asm_proc(path, function_name)

        if exact:
            exact["relative_path"] = relative_string(path, donor_root)
            report["exact_matches"].append(exact)
            continue

        if ref_budget <= 0:
            continue

        refs = find_references(path, function_name, ref_budget)
        for ref in refs:
            ref["relative_path"] = relative_string(path, donor_root)
            report["reference_hits"].append(ref)
        ref_budget -= len(refs)

    return report


def build_support_symbol_report(function_name, asm_source, donor_dir, max_symbols=6, max_refs=4, lst_source=None, map_file=None):
    asm_text = extract_asm_function_text(Path(asm_source), function_name)
    if not asm_text and lst_source and map_file:
        asm_text = extract_asm_function_from_lst(lst_source, map_file, function_name)
    if not asm_text:
        return {
            "function": function_name,
            "asm_source": str(asm_source),
            "support_symbols": [],
        }

    symbols = extract_called_symbols_from_asm_text(asm_text)
    support = []
    for symbol in symbols[:max_symbols]:
        donor = build_donor_report(symbol, donor_dir, max_refs=max_refs)
        if donor["exact_matches"] or donor["reference_hits"]:
            support.append(
                {
                    "symbol": symbol,
                    "exact_match_count": len(donor["exact_matches"]),
                    "reference_hit_count": len(donor["reference_hits"]),
                    "best_exact_match": donor["exact_matches"][0] if donor["exact_matches"] else None,
                    "best_reference_hit": donor["reference_hits"][0] if donor["reference_hits"] else None,
                }
            )
    return {
        "function": function_name,
        "asm_source": str(asm_source),
        "support_symbols": support,
    }


def render_context_text(report):
    lines = []
    lines.append(f"Donor project hints for {report['function']}")
    lines.append(f"Donor root: {report['donor_dir']}")

    if report["exact_matches"]:
        lines.append("")
        lines.append("Exact function matches:")
        for match in report["exact_matches"]:
            lines.append(
                f"- {match['kind']} in {match['relative_path']}:{match['start_line']}-{match['end_line']}"
            )
            lines.append("```text")
            lines.append(match["snippet"].rstrip())
            lines.append("```")
    else:
        lines.append("")
        lines.append("Exact function matches: none found")

    if report["reference_hits"]:
        lines.append("")
        lines.append("Reference hits:")
        for hit in report["reference_hits"]:
            lines.append(f"- {hit['relative_path']}:{hit['line']}: {hit['text'].strip()}")
    else:
        lines.append("")
        lines.append("Reference hits: none found")

    return "\n".join(lines).rstrip() + "\n"


def render_brief_text(report):
    exact_count = len(report["exact_matches"])
    ref_count = len(report["reference_hits"])
    if exact_count:
        first = report["exact_matches"][0]
        return (
            f"donor: {exact_count} exact match(es), {ref_count} reference hit(s); "
            f"best match {first['relative_path']}:{first['start_line']}"
        )
    if ref_count:
        first = report["reference_hits"][0]
        return f"donor: no exact match, {ref_count} reference hit(s); first {first['relative_path']}:{first['line']}"
    return "donor: no exact match and no reference hits"


def render_support_brief_text(report):
    support = report["support_symbols"]
    if not support:
        return "donor support: no supporting symbol hits"

    pieces = []
    for item in support[:3]:
        if item["best_exact_match"]:
            match = item["best_exact_match"]
            pieces.append(f"{item['symbol']} -> {match['relative_path']}:{match['start_line']}")
        elif item["best_reference_hit"]:
            hit = item["best_reference_hit"]
            pieces.append(f"{item['symbol']} -> {hit['relative_path']}:{hit['line']}")
    return "donor support: " + "; ".join(pieces)


def main():
    parser = argparse.ArgumentParser(description="Search donor source trees for exact or nearby function matches.")
    parser.add_argument("--function", required=True, help="Function name to look for")
    parser.add_argument("--donor-dir", required=True, help="Donor source tree root")
    parser.add_argument("--max-refs", type=int, default=8, help="Maximum total reference hits (default: %(default)s)")
    parser.add_argument("--asm-source", help="Optional asm source to inspect for called helper symbols")
    parser.add_argument("--lst-source", help="Optional listing fallback when the function is absent from --asm-source")
    parser.add_argument("--map-file", help="Map file used together with --lst-source")
    parser.add_argument("--support-symbols", action="store_true", help="Search donor code for helper symbols called by the asm routine")
    parser.add_argument("--max-symbols", type=int, default=6, help="Maximum called symbols to inspect (default: %(default)s)")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument("--brief", action="store_true", help="Emit a one-line summary")
    args = parser.parse_args()

    if args.support_symbols:
        if not args.asm_source:
            raise SystemExit("--asm-source is required with --support-symbols")
        report = build_support_symbol_report(
            args.function,
            args.asm_source,
            args.donor_dir,
            max_symbols=args.max_symbols,
            max_refs=args.max_refs,
            lst_source=args.lst_source,
            map_file=args.map_file,
        )
    else:
        report = build_donor_report(args.function, args.donor_dir, max_refs=args.max_refs)
    if args.json:
        print(json.dumps(report, indent=2))
        return
    if args.brief:
        if args.support_symbols:
            print(render_support_brief_text(report))
        else:
            print(render_brief_text(report))
        return
    if args.support_symbols:
        print(json.dumps(report, indent=2))
        return
    print(render_context_text(report), end="")


if __name__ == "__main__":
    main()
