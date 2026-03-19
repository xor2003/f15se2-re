#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
MAP_SEGMENT_RE = re.compile(r"^(\w+)\s+CODE\s+([0-9a-fA-F]+)")
MAP_ROUTINE_RE = re.compile(r"^([\w_]+):\s+(\w+)\s+(NEAR|FAR)\s+([0-9a-fA-F]+)-([0-9a-fA-F]+)(?:\s+(.*))?$")
SECTION_RE = re.compile(
    r"^--- Now @([0-9a-fA-F]{4}):([0-9a-fA-F]{4})/([0-9a-fA-F]+), routine "
    r"([0-9a-fA-F]{4}):([0-9a-fA-F]{4})-([0-9a-fA-F]{4}):([0-9a-fA-F]{4})\[[0-9a-fA-F]+\]: "
    r"([\w_]+).* target @([0-9a-fA-F]{4}):([0-9a-fA-F]{4})/([0-9a-fA-F]+)"
)
COMPARE_RE = re.compile(
    r"^(MATCH|DIFF_OP1|DIFF_OP2|DIFF_MAP|MISMATCH):\s+"
    r"([0-9a-fA-F]{4}):([0-9a-fA-F]{4})/([0-9a-fA-F]+):\s*(.*?)\s+"
    r"(==|~=|=~|~~|!=)\s+"
    r"([0-9a-fA-F]{4}):([0-9a-fA-F]{4})/([0-9a-fA-F]+):\s*(.*)$"
)
ERROR_RE = re.compile(r"^ERROR: Instruction mismatch in routine ([\w_]+) at (.*)$")
SUMMARY_RESULT_RE = re.compile(r'^result: "([^"]+)"$')
SUMMARY_ROUTINES_RE = re.compile(r"^routines_compared:\s+(\d+)$")
SUMMARY_MATCHED_RE = re.compile(r"^instructions_matched:\s+(\d+)$")
SUMMARY_FIRST_ROUTINE_RE = re.compile(r'^\s*"routine":\s*"([^"]+)",?$')
SUMMARY_FIRST_ADDR_RE = re.compile(r'^\s*"ref_addr":\s*"([^"]+)",?$')
SUMMARY_FIRST_DETAILS_RE = re.compile(r'^\s*"details":\s*"([^"]+)",?$')
LST_LINE_RE = re.compile(r"^(\w+):([0-9a-fA-F]{4})\s+(.*)$")
COD_FUNC_RE = re.compile(r"^_?(\w+)\s+PROC\b", re.I)
COD_LINE_RE = re.compile(r"; Line (\d+)")
COD_SOURCE_RE = re.compile(r";\|\*\*\*\s?(.*)")
COD_ASM_RE = re.compile(r"^\s*\*\*\*\s+([0-9a-fA-F]{6})\s+([0-9a-fA-F\s]+?)\s+(.*)")
C_FUNC_RE = re.compile(
    r"^\s*(?:unsigned\s+)?(?:void|char|int|long|__int\d+)\s+(?:__cdecl\s+)?(?:far\s+)?(\w+)\s*\([^;{}]*\)\s*\{",
    re.M,
)


def strip_ansi(text):
    return ANSI_RE.sub("", text)


def linear(seg_base, offset):
    return (seg_base << 4) + offset


def parse_map_file(path):
    segments = {}
    routines = []
    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if match := MAP_SEGMENT_RE.match(line):
            segments[match.group(1)] = int(match.group(2), 16)
            continue
        if match := MAP_ROUTINE_RE.match(line):
            seg_name = match.group(2)
            seg_base = segments.get(seg_name)
            if seg_base is None:
                continue
            begin = int(match.group(4), 16)
            end = int(match.group(5), 16)
            routines.append(
                {
                    "name": match.group(1),
                    "segment": seg_name,
                    "begin": begin,
                    "end": end,
                    "begin_linear": linear(seg_base, begin),
                    "end_linear": linear(seg_base, end),
                    "attrs": sorted(set((match.group(6) or "").split())),
                }
            )
    return routines


def parse_c_functions(src_dir):
    owners = {}
    for path in sorted(Path(src_dir).glob("*.c")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in C_FUNC_RE.findall(text):
            owners.setdefault(name, []).append(path)
    return owners


def find_cod_for_function(function_name, c_owners, src_dir):
    for c_path in c_owners.get(function_name, []):
        cod_path = c_path.with_suffix(".COD")
        upper_cod = cod_path.with_name(cod_path.stem.upper() + ".COD")
        if upper_cod.exists():
            return upper_cod
        if cod_path.exists():
            return cod_path
    for cod_path in sorted(Path(src_dir).glob("*.COD")):
        text = cod_path.read_text(encoding="cp437", errors="replace")
        if re.search(rf"^_{re.escape(function_name)}\s+PROC\b", text, re.M):
            return cod_path
    return None


def parse_cod_file(path):
    functions = {}
    current_function = None
    current_line = None
    current_source = ""
    for raw_line in Path(path).read_text(encoding="cp437", errors="replace").splitlines():
        if match := COD_FUNC_RE.match(raw_line.strip()):
            current_function = match.group(1)
            functions.setdefault(current_function, {"lines": []})
            current_line = None
            current_source = ""
            continue
        if match := COD_SOURCE_RE.match(raw_line):
            current_source = match.group(1).strip()
            continue
        if match := COD_LINE_RE.search(raw_line):
            current_line = {
                "line_num": int(match.group(1)),
                "c_code": current_source,
                "assembly": [],
            }
            if current_function:
                functions[current_function]["lines"].append(current_line)
            continue
        if current_function and current_line:
            if match := COD_ASM_RE.match(raw_line):
                current_line["assembly"].append(
                    {
                        "address": int(match.group(1), 16),
                        "instruction": match.group(3).strip(),
                    }
                )
    return functions


def find_cod_line(function_name, cod_path, relative_addr):
    if cod_path is None or not cod_path.exists():
        return None
    functions = parse_cod_file(cod_path)
    func = functions.get(function_name)
    if not func:
        return None
    nearest = None
    nearest_delta = None
    for item in func["lines"]:
        for asm_line in item["assembly"]:
            if asm_line["address"] == relative_addr:
                return item
            delta = abs(asm_line["address"] - relative_addr)
            if nearest_delta is None or delta < nearest_delta:
                nearest = dict(item)
                nearest["nearest_address"] = asm_line["address"]
                nearest["nearest_delta"] = delta
                nearest_delta = delta
    return nearest


def parse_lst_file(path):
    instructions = {}
    for raw_line in Path(path).read_text(encoding="cp437", errors="replace").splitlines():
        match = LST_LINE_RE.match(raw_line)
        if not match:
            continue
        segment = match.group(1)
        offset = int(match.group(2), 16)
        remainder = match.group(3).strip()
        if not remainder:
            continue
        instr = remainder.split(";", 1)[0].strip()
        if not instr or instr.endswith("segment") or instr == "ends":
            continue
        instructions[(segment, offset)] = instr
    return instructions


def parse_mzdiff_output(path):
    records = []
    hard_errors = []
    summary = {}
    current = None
    in_first_mismatch = False

    for raw_line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = strip_ansi(raw_line).rstrip()
        if not line:
            continue
        if match := SECTION_RE.match(line):
            current = {
                "routine": match.group(8),
                "ref_start_linear": int(match.group(3), 16),
                "tgt_start_linear": int(match.group(11), 16),
            }
            continue
        if match := COMPARE_RE.match(line):
            status = match.group(1)
            records.append(
                {
                    "routine": current["routine"] if current else None,
                    "ref_addr_linear": int(match.group(4), 16),
                    "ref_instr": match.group(5).strip(),
                    "tgt_addr_linear": int(match.group(9), 16),
                    "tgt_instr": match.group(10).split("//", 1)[0].strip(),
                    "status": status,
                    "routine_ref_start_linear": current["ref_start_linear"] if current else None,
                    "routine_tgt_start_linear": current["tgt_start_linear"] if current else None,
                }
            )
            continue
        if match := ERROR_RE.match(line):
            hard_errors.append({"routine": match.group(1), "text": match.group(2)})
            continue
        if line == "[SUMMARY_START]":
            in_first_mismatch = False
            continue
        if match := SUMMARY_RESULT_RE.match(line):
            summary["result"] = match.group(1)
            continue
        if match := SUMMARY_ROUTINES_RE.match(line):
            summary["routines_compared"] = int(match.group(1))
            continue
        if match := SUMMARY_MATCHED_RE.match(line):
            summary["instructions_matched"] = int(match.group(1))
            continue
        if line.startswith("first_mismatch:"):
            summary["first_mismatch"] = {}
            in_first_mismatch = True
            continue
        if in_first_mismatch:
            if line == "}":
                in_first_mismatch = False
                continue
            if match := SUMMARY_FIRST_ROUTINE_RE.match(line):
                summary["first_mismatch"]["routine"] = match.group(1)
            elif match := SUMMARY_FIRST_ADDR_RE.match(line):
                summary["first_mismatch"]["ref_addr"] = match.group(1)
            elif match := SUMMARY_FIRST_DETAILS_RE.match(line):
                summary["first_mismatch"]["details"] = match.group(1)
    return records, hard_errors, summary


def routine_by_name(routines, name):
    for routine in routines:
        if routine["name"] == name:
            return routine
    return None


def summarize(records, top):
    counts = {}
    hardish = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
        routine = record["routine"] or "<unknown>"
        hardish[routine] = hardish.get(routine, 0) + (0 if record["status"] == "MATCH" else 1)
    top_routines = sorted(hardish.items(), key=lambda item: (-item[1], item[0]))[:top]
    return counts, top_routines


def enrich_hard_errors(hard_errors, records, routines, c_owners, src_dir):
    enriched = []
    for error in hard_errors:
        routine_name = error["routine"]
        routine = routine_by_name(routines, routine_name)
        relevant = None
        if match := COMPARE_RE.match(error["text"]):
            ref_addr_linear = int(match.group(4), 16)
            tgt_addr_linear = int(match.group(9), 16)
            relevant = next(
                (
                    r
                    for r in records
                    if r["routine"] == routine_name
                    and r["ref_addr_linear"] == ref_addr_linear
                    and r["tgt_addr_linear"] == tgt_addr_linear
                ),
                None,
            )
        if relevant is None:
            relevant = next((r for r in records if r["routine"] == routine_name and r["status"] != "MATCH"), None)
        c_files = [str(path) for path in c_owners.get(routine_name, [])]
        cod_path = find_cod_for_function(routine_name, c_owners, src_dir)
        cod_line = None
        rel = None
        if relevant and relevant["routine_tgt_start_linear"] is not None:
            rel = relevant["tgt_addr_linear"] - relevant["routine_tgt_start_linear"]
            cod_line = find_cod_line(routine_name, cod_path, rel)
        item = {
            "routine": routine_name,
            "map_routine": routine,
            "relevant_record": relevant,
            "c_files": c_files,
            "cod_path": str(cod_path) if cod_path else None,
            "target_relative_offset": rel,
            "cod_line": cod_line,
        }
        enriched.append(item)
    return enriched


def report_hard_errors(enriched, function_filter=None):
    visible = enriched
    hidden_count = 0
    if function_filter:
        visible = [item for item in enriched if item["routine"] == function_filter]
        hidden_count = len(enriched) - len(visible)

    if not visible:
        print("No hard instruction mismatches found.")
        if hidden_count:
            print(f"(suppressed {hidden_count} hard mismatches outside {function_filter})")
        return

    print("Hard mismatches:")
    for item in visible:
        print(f"- {item['routine']}")
        routine = item["map_routine"]
        relevant = item["relevant_record"]
        if routine:
            print(f"  ref range: {routine['segment']}:{routine['begin']:04x}-{routine['end']:04x}")
        if relevant:
            print(f"  first diff: {relevant['status']} ref={relevant['ref_instr']} tgt={relevant['tgt_instr']}")
        if item["c_files"]:
            print(f"  C owner: {', '.join(item['c_files'])}")
        if item["cod_path"]:
            print(f"  COD: {item['cod_path']}")
        if item["target_relative_offset"] is not None:
            print(f"  target relative offset: 0x{item['target_relative_offset']:x}")
        cod_line = item["cod_line"]
        if cod_line:
            print(f"  likely C line: {cod_line['line_num']}: {cod_line['c_code']}")
            if "nearest_delta" in cod_line and cod_line["nearest_delta"] != 0:
                print(
                    f"  nearest COD addr: 0x{cod_line['nearest_address']:x} "
                    f"(delta 0x{cod_line['nearest_delta']:x})"
                )
    if hidden_count:
        print(f"(suppressed {hidden_count} hard mismatches outside {function_filter})")


def report_soft_diffs(records, routines, c_owners, src_dir, function_filter, top):
    filtered = [r for r in records if r["status"] != "MATCH"]
    if function_filter:
        filtered = [r for r in filtered if r["routine"] == function_filter]
    if not filtered:
        print("No soft diffs to report.")
        return

    shown = 0
    print("Soft diff samples:")
    for record in filtered:
        routine_name = record["routine"] or "<unknown>"
        cod_path = find_cod_for_function(routine_name, c_owners, src_dir)
        rel = None
        cod_line = None
        if record["routine_tgt_start_linear"] is not None:
            rel = record["tgt_addr_linear"] - record["routine_tgt_start_linear"]
            cod_line = find_cod_line(routine_name, cod_path, rel)
        print(f"- {routine_name}: {record['status']} @ ref 0x{record['ref_addr_linear']:x} tgt 0x{record['tgt_addr_linear']:x}")
        print(f"  ref: {record['ref_instr']}")
        print(f"  tgt: {record['tgt_instr']}")
        if cod_line:
            print(f"  C: line {cod_line['line_num']}: {cod_line['c_code']}")
            if "nearest_delta" in cod_line and cod_line["nearest_delta"] != 0:
                print(
                    f"  nearest COD addr: 0x{cod_line['nearest_address']:x} "
                    f"(delta 0x{cod_line['nearest_delta']:x})"
                )
        shown += 1
        if shown >= top:
            break


def main():
    parser = argparse.ArgumentParser(description="Correlate mzdiff output with map, lst, and MSC .COD listings.")
    parser.add_argument("mzdiff_file", help="Path to a saved mzdiff output file")
    parser.add_argument("--map-file", required=True, help="Reference map file")
    parser.add_argument("--lst-file", help="IDA .lst file for original asm context")
    parser.add_argument("--src-dir", default="src", help="Source directory containing .c and .COD files")
    parser.add_argument("--function", help="Focus on a single function")
    parser.add_argument("--top", type=int, default=8, help="How many routines/diffs to show")
    parser.add_argument("--json", action="store_true", help="Emit parsed summary as JSON")
    args = parser.parse_args()

    routines = parse_map_file(args.map_file)
    records, hard_errors, summary = parse_mzdiff_output(args.mzdiff_file)
    c_owners = parse_c_functions(args.src_dir)
    counts, top_routines = summarize(records, args.top)
    enriched_hard_errors = enrich_hard_errors(hard_errors, records, routines, c_owners, args.src_dir)

    if args.json:
        print(
            json.dumps(
                {
                    "summary": summary,
                    "counts": counts,
                    "hard_errors": enriched_hard_errors,
                    "top_routines": top_routines,
                },
                indent=2,
            )
        )
        return

    print("mzdiff summary:")
    print(f"- result: {summary.get('result', 'unknown')}")
    print(f"- routines compared: {summary.get('routines_compared', 'unknown')}")
    print(f"- instructions matched: {summary.get('instructions_matched', 'unknown')}")
    if "first_mismatch" in summary:
        fm = summary["first_mismatch"]
        print(f"- first missed routine from summary: {fm.get('routine')} ({fm.get('details')})")

    print("Diff counts:")
    for key in sorted(counts):
        print(f"- {key}: {counts[key]}")

    print("Top routines by diff count:")
    for routine_name, count in top_routines:
        print(f"- {routine_name}: {count}")

    report_hard_errors(enriched_hard_errors, args.function)
    report_soft_diffs(records, routines, c_owners, args.src_dir, args.function, args.top)


if __name__ == "__main__":
    main()
