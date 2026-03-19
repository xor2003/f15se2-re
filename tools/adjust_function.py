#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from correlation_analyzer import (  # noqa: E402
    enrich_hard_errors,
    find_cod_line,
    find_cod_for_function,
    parse_c_functions,
    parse_cod_file,
    parse_lst_file,
    parse_map_file,
    parse_mzdiff_output,
    summarize,
)

SEG_COMMENT_RE = re.compile(r"seg([0-9A-Fa-f]{3}):(?:0x)?([0-9A-Fa-f]{4})")
MNEMONIC_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9]*)\b")


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, check=False)


def run_capture(cmd):
    return subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)


def pick_focus(function_name, hard_errors, records, top_routines):
    if function_name:
        hard = next((item for item in hard_errors if item["routine"] == function_name), None)
        if hard:
            return function_name, "hard", hard
        soft = next((item for item in records if item["routine"] == function_name and item["status"] != "MATCH"), None)
        if soft:
            return function_name, "soft", soft
        return function_name, "missing", None

    if hard_errors:
        return hard_errors[0]["routine"], "hard", hard_errors[0]
    first_soft = next((item for item in records if item["status"] != "MATCH" and item["routine"]), None)
    if first_soft:
        return first_soft["routine"], "soft", first_soft
    if top_routines:
        return top_routines[0][0], "inspect", None
    return None, "missing", None


def read_source_window(path, center_line, radius):
    if not path or center_line is None:
        return []
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, center_line - radius)
    end = min(len(lines), center_line + radius)
    return [{"line_num": idx, "text": lines[idx - 1]} for idx in range(start, end + 1)]


def find_source_anchor(path, center_line):
    if not path or center_line is None:
        return None
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    best = None
    for idx, line in enumerate(lines, start=1):
        if idx > center_line:
            break
        match = SEG_COMMENT_RE.search(line)
        if not match:
            continue
        best = {
            "line_num": idx,
            "segment": f"seg{match.group(1).lower()}",
            "offset": int(match.group(2), 16),
            "text": line.strip(),
        }
    return best


def lst_window(lst_path, segment, center_offset, radius):
    lines = []
    start = max(0, center_offset - radius)
    end = center_offset + radius
    for raw_line in Path(lst_path).read_text(encoding="cp437", errors="replace").splitlines():
        if not raw_line.startswith(f"{segment}:"):
            continue
        try:
            offset = int(raw_line[len(segment) + 1 : len(segment) + 5], 16)
        except ValueError:
            continue
        if start <= offset <= end:
            lines.append({"offset": offset, "text": raw_line.rstrip()})
    return lines


def cod_window(cod_path, function_name, center_line_num, radius):
    if not cod_path:
        return []
    functions = parse_cod_file(cod_path)
    func = functions.get(function_name)
    if not func:
        return []
    if center_line_num is None:
        return func["lines"][:radius]
    candidates = [idx for idx, item in enumerate(func["lines"]) if item["line_num"] == center_line_num]
    if not candidates:
        nearest = min(
            range(len(func["lines"])),
            key=lambda idx: abs(func["lines"][idx]["line_num"] - center_line_num),
        )
        center_index = nearest
    else:
        center_index = candidates[0]
    start = max(0, center_index - radius)
    end = min(len(func["lines"]), center_index + radius + 1)
    return func["lines"][start:end]


def extract_mnemonic(instr_text):
    text = instr_text.split(";", 1)[0].strip().lower()
    match = MNEMONIC_RE.search(text)
    return match.group(1) if match else ""


def lst_mnemonics(entries):
    mnemonics = []
    for item in entries:
        parts = item["text"].split(None, 1)
        if len(parts) < 2:
            continue
        rest = parts[1]
        mnemonic = extract_mnemonic(rest)
        if mnemonic:
            mnemonics.append(mnemonic)
    return mnemonics


def lst_instruction_stream(entries):
    out = []
    for item in entries:
        parts = item["text"].split(None, 1)
        if len(parts) < 2:
            continue
        rest = parts[1]
        mnemonic = extract_mnemonic(rest)
        if not mnemonic:
            continue
        out.append({"offset": item["offset"], "text": rest, "mnemonic": mnemonic})
    return out


def cod_instruction_stream(cod_entries):
    out = []
    for entry in cod_entries:
        for asm in entry["assembly"]:
            mnemonic = extract_mnemonic(asm["instruction"])
            if not mnemonic:
                continue
            out.append(
                {
                    "line_num": entry["line_num"],
                    "c_code": entry["c_code"],
                    "address": asm["address"],
                    "instruction": asm["instruction"],
                    "mnemonic": mnemonic,
                }
            )
    return out


def find_best_cod_block_match(cod_path, function_name, anchor_lst_entries, center_address=None, max_distance=0x80):
    if not cod_path or not anchor_lst_entries:
        return None
    functions = parse_cod_file(cod_path)
    func = functions.get(function_name)
    if not func:
        return None

    ref_mnemonics = lst_mnemonics(anchor_lst_entries)
    if len(ref_mnemonics) < 4:
        return None

    cod_stream = cod_instruction_stream(func["lines"])
    if len(cod_stream) < len(ref_mnemonics):
        return None

    best = None
    window_len = min(len(ref_mnemonics), 16)
    ref_slice = ref_mnemonics[:window_len]
    for start in range(0, len(cod_stream) - window_len + 1):
        window = cod_stream[start : start + window_len]
        if center_address is not None:
            if abs(window[0]["address"] - center_address) > max_distance and abs(window[-1]["address"] - center_address) > max_distance:
                continue
        score = sum(1 for idx in range(window_len) if window[idx]["mnemonic"] == ref_slice[idx])
        if best is None or score > best["score"]:
            best = {
                "score": score,
                "window_len": window_len,
                "start_index": start,
                "start_address": window[0]["address"],
                "end_address": window[-1]["address"],
                "line_num": window[0]["line_num"],
                "items": window,
            }
    if not best or best["score"] == 0:
        return None
    return best


def find_best_cod_block_match_from_entries(cod_entries, anchor_lst_entries):
    if not cod_entries or not anchor_lst_entries:
        return None
    ref_mnemonics = lst_mnemonics(anchor_lst_entries)
    if len(ref_mnemonics) < 4:
        return None
    cod_stream = cod_instruction_stream(cod_entries)
    if len(cod_stream) < 4:
        return None
    best = None
    window_len = min(len(ref_mnemonics), len(cod_stream), 16)
    ref_slice = ref_mnemonics[:window_len]
    for start in range(0, len(cod_stream) - window_len + 1):
        window = cod_stream[start : start + window_len]
        score = sum(1 for idx in range(window_len) if window[idx]["mnemonic"] == ref_slice[idx])
        if best is None or score > best["score"]:
            best = {
                "score": score,
                "window_len": window_len,
                "start_index": start,
                "start_address": window[0]["address"],
                "end_address": window[-1]["address"],
                "line_num": window[0]["line_num"],
                "items": window,
            }
    if not best or best["score"] == 0:
        return None
    return best


def collect_soft_diffs(records, function_name, limit):
    return [item for item in records if item["routine"] == function_name and item["status"] != "MATCH"][:limit]


def heuristic_notes(focus_kind, record_or_error, soft_diffs):
    notes = []
    if focus_kind == "hard" and record_or_error and record_or_error.get("relevant_record"):
        record = record_or_error["relevant_record"]
        ref_instr = record["ref_instr"]
        tgt_instr = record["tgt_instr"]
        if ref_instr.startswith("call ") and tgt_instr.startswith("call "):
            notes.append("The first hard mismatch is a call target difference, so the surrounding control flow is diverging before the call site.")
        if ref_instr.startswith("jmp ") or tgt_instr.startswith("jmp "):
            notes.append("A branch shape mismatch usually means the preceding condition compiled differently, not just the jump itself.")
    if soft_diffs:
        first = soft_diffs[0]
        if first["status"] in {"DIFF_OP1", "DIFF_OP2"}:
            notes.append("Early operand diffs often mean the compiler changed store order, temporary lifetimes, or signedness before the first hard mismatch.")
        if len(soft_diffs) >= 3 and len({item["tgt_instr"] for item in soft_diffs[:3]}) >= 2:
            notes.append("Multiple nearby soft diffs suggest reworking the whole local expression/block, not only the exact failing line.")
    if not notes:
        notes.append("Start from the first reported C line and inspect the preceding block for control-flow or temporary-shape differences.")
    return notes


def add_alignment_notes(notes, source_anchor, mismatch_reference_offset):
    if not source_anchor:
        notes.append("No seg000-style source anchor comment was found near the current C line, so reference asm is aligned from the mismatch address only.")
        return notes
    notes.append(
        f"Using source anchor {source_anchor['segment']}:{source_anchor['offset']:04x} from C line {source_anchor['line_num']} to align the reference asm window."
    )
    if mismatch_reference_offset is not None:
        delta = abs(mismatch_reference_offset - source_anchor["offset"])
        if delta > 0x20:
            notes.append(
                f"The first hard mismatch is 0x{delta:x} bytes away from the source anchor, so the generated function has already drifted beyond this C block."
            )
    return notes


def add_block_match_notes(notes, block_match, label="Best mnemonic-level .COD block match"):
    if not block_match:
        notes.append("No useful mnemonic-level block match was found between the source-anchored reference asm and generated .COD.")
        return notes
    notes.append(
        f"{label} starts near 0x{block_match['start_address']:x} "
        f"(score {block_match['score']}/{block_match['window_len']})."
    )
    return notes


def jump_family(mnemonic):
    signed = {"jg", "jge", "jl", "jle"}
    unsigned = {"ja", "jae", "jb", "jbe"}
    if mnemonic in signed:
        return "signed"
    if mnemonic in unsigned:
        return "unsigned"
    return None


def add_shape_notes(notes, anchor_lst_entries, block_match):
    if not anchor_lst_entries or not block_match:
        return notes

    ref_stream = lst_instruction_stream(anchor_lst_entries)
    cod_stream = block_match["items"]
    compare_len = min(len(ref_stream), len(cod_stream), 20)
    if compare_len == 0:
        return notes

    ref_jumps = [item["mnemonic"] for item in ref_stream[:compare_len] if item["mnemonic"].startswith("j")]
    cod_jumps = [item["mnemonic"] for item in cod_stream[:compare_len] if item["mnemonic"].startswith("j")]
    for ref_mn, cod_mn in zip(ref_jumps, cod_jumps):
        ref_family = jump_family(ref_mn)
        cod_family = jump_family(cod_mn)
        if ref_family and cod_family and ref_family != cod_family:
            notes.append(
                f"Branch signedness drift detected in the matched block ({ref_mn} vs {cod_mn}); check types and comparisons in the surrounding C condition."
            )
            break

    ref_movs = sum(1 for item in ref_stream[:compare_len] if item["mnemonic"] == "mov")
    cod_movs = sum(1 for item in cod_stream[:compare_len] if item["mnemonic"] == "mov")
    if cod_movs >= ref_movs + 2:
        notes.append("The generated block uses extra mov instructions compared to the reference, which often means an avoidable temporary or split expression.")

    ref_pushes = sum(1 for item in ref_stream[:compare_len] if item["mnemonic"] == "push")
    cod_pushes = sum(1 for item in cod_stream[:compare_len] if item["mnemonic"] == "push")
    if cod_pushes >= ref_pushes + 2:
        notes.append("The generated block materializes more stack arguments than the reference; try simplifying the local expression or reducing temporaries around the call.")

    ref_has_signed_div = any(item["mnemonic"] in {"cwd", "idiv"} for item in ref_stream[:compare_len])
    cod_has_signed_div = any(item["mnemonic"] in {"cwd", "idiv"} for item in cod_stream[:compare_len])
    if cod_has_signed_div and not ref_has_signed_div:
        notes.append("The generated block introduced signed division/sign-extension instructions not seen in the matched reference window; recheck signedness and integer promotion.")

    return notes


def add_expression_notes(notes, c_window, cod_window):
    c_text = "\n".join(item["text"] for item in c_window)
    cod_c_text = "\n".join(item["c_code"] for item in cod_window if item["c_code"])
    cod_instrs = [asm["instruction"] for entry in cod_window for asm in entry["assembly"]]
    cod_mnemonics = [extract_mnemonic(instr) for instr in cod_instrs]

    if any(mn in {"cwd", "idiv"} for mn in cod_mnemonics):
        if "/" in c_text or "/" in cod_c_text:
            notes.append("Signed divide/sign-extension is present in the generated block; keep casts and operand signedness extremely explicit around the division expression.")

    if any(mn in {"inc", "dec"} for mn in cod_mnemonics):
        if "++" in c_text or "--" in c_text or "++" in cod_c_text or "--" in cod_c_text:
            notes.append("Increment/decrement side effects occur inside the generated block; consider splitting them into separate statements if evaluation order looks wrong.")

    if cod_mnemonics.count("jmp") >= 2 and ("?" in c_text or "?" in cod_c_text):
        notes.append("The current logic compiles into multiple jumps around a conditional expression; an explicit if/else may give closer branch shape than a ternary.")

    if cod_mnemonics.count("push") >= 4 and cod_mnemonics.count("call") >= 2:
        notes.append("This region is argument-heavy and call-heavy; reducing nested expressions or reusing simple locals may help MSC keep the call sequence closer to the reference.")

    return notes


def render_report(bundle):
    print(f"Focus routine: {bundle['function']}")
    print(f"Focus kind: {bundle['focus_kind']}")
    if bundle["c_file"]:
        print(f"C file: {bundle['c_file']}")
    if bundle["cod_path"]:
        print(f"COD: {bundle['cod_path']}")
    if bundle["target_relative_offset"] is not None:
        print(f"Target relative offset: 0x{bundle['target_relative_offset']:x}")
    if bundle["reference_offset"] is not None:
        print(f"Reference mismatch offset: 0x{bundle['reference_offset']:x}")
    if bundle["source_anchor"]:
        print(
            f"Reference source anchor: {bundle['source_anchor']['segment']}:{bundle['source_anchor']['offset']:04x} "
            f"(C line {bundle['source_anchor']['line_num']})"
        )

    print("Notes:")
    for note in bundle["notes"]:
        print(f"- {note}")

    if bundle["focus_record"]:
        print("Focus diff:")
        print(f"- status: {bundle['focus_record']['status']}")
        print(f"- ref: {bundle['focus_record']['ref_instr']}")
        print(f"- tgt: {bundle['focus_record']['tgt_instr']}")

    if bundle["c_window"]:
        print("C window:")
        for item in bundle["c_window"]:
            print(f"{item['line_num']:5d}: {item['text']}")

    if bundle["cod_window"]:
        print("COD window:")
        for item in bundle["cod_window"]:
            print(f"- line {item['line_num']}: {item['c_code']}")
            for asm in item["assembly"]:
                print(f"    0x{asm['address']:04x}: {asm['instruction']}")

    if bundle["preferred_cod_block_match"]:
        match = bundle["preferred_cod_block_match"]
        print(
            f"Best COD block match: line {match['line_num']}, "
            f"0x{match['start_address']:04x}-0x{match['end_address']:04x}, "
            f"score {match['score']}/{match['window_len']}"
        )
        for item in match["items"]:
            print(f"    0x{item['address']:04x}: {item['instruction']}")

    if bundle["anchor_lst_window"]:
        print("Reference asm window (source anchor):")
        for item in bundle["anchor_lst_window"]:
            print(f"0x{item['offset']:04x}: {item['text']}")

    if bundle["mismatch_lst_window"]:
        print("Reference asm window (first mismatch):")
        for item in bundle["mismatch_lst_window"]:
            print(f"0x{item['offset']:04x}: {item['text']}")

    if bundle["soft_diffs"]:
        print("Nearby soft diffs:")
        for item in bundle["soft_diffs"]:
            print(f"- {item['status']} ref=0x{item['ref_addr_linear']:x} tgt=0x{item['tgt_addr_linear']:x}")
            print(f"  ref: {item['ref_instr']}")
            print(f"  tgt: {item['tgt_instr']}")


def build_llm_prompt(bundle):
    lines = []
    lines.append("Adjust the C code for this MSC 5.1 decompilation routine to move it closer to binary identity.")
    lines.append("Make the smallest possible source changes in the shown C region.")
    lines.append("Prefer compiler-shape fidelity over readability cleanup.")
    lines.append("")
    lines.append(f"Routine: {bundle['function']}")
    lines.append(f"Focus kind: {bundle['focus_kind']}")
    if bundle["target_relative_offset"] is not None:
        lines.append(f"Target relative offset: 0x{bundle['target_relative_offset']:x}")
    if bundle["source_anchor"]:
        lines.append(
            f"Reference source anchor: {bundle['source_anchor']['segment']}:{bundle['source_anchor']['offset']:04x} "
            f"(C line {bundle['source_anchor']['line_num']})"
        )
    lines.append("")
    lines.append("Diagnostic notes:")
    for note in bundle["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    if bundle["focus_record"]:
        lines.append("First focused diff:")
        lines.append(f"- status: {bundle['focus_record']['status']}")
        lines.append(f"- ref: {bundle['focus_record']['ref_instr']}")
        lines.append(f"- tgt: {bundle['focus_record']['tgt_instr']}")
        lines.append("")
    if bundle["c_window"]:
        lines.append("Current C window:")
        lines.append("```c")
        for item in bundle["c_window"]:
            lines.append(f"{item['line_num']:5d}: {item['text']}")
        lines.append("```")
        lines.append("")
    if bundle["cod_window"]:
        lines.append("Generated MSC .COD window:")
        lines.append("```text")
        for item in bundle["cod_window"]:
            lines.append(f"line {item['line_num']}: {item['c_code']}")
            for asm in item["assembly"]:
                lines.append(f"  0x{asm['address']:04x}: {asm['instruction']}")
        lines.append("```")
        lines.append("")
    if bundle["anchor_lst_window"]:
        lines.append("Original reference asm near the source anchor:")
        lines.append("```asm")
        for item in bundle["anchor_lst_window"]:
            lines.append(item["text"])
        lines.append("```")
        lines.append("")
    if bundle["preferred_cod_block_match"]:
        match = bundle["preferred_cod_block_match"]
        lines.append("Best mnemonic-level generated .COD block match:")
        lines.append("```text")
        lines.append(
            f"line {match['line_num']}, 0x{match['start_address']:04x}-0x{match['end_address']:04x}, "
            f"score {match['score']}/{match['window_len']}"
        )
        for item in match["items"]:
            lines.append(f"  0x{item['address']:04x}: {item['instruction']}")
        lines.append("```")
        lines.append("")
    if bundle["soft_diffs"]:
        lines.append("Nearby soft diffs:")
        lines.append("```text")
        for item in bundle["soft_diffs"]:
            lines.append(f"{item['status']} ref=0x{item['ref_addr_linear']:x} tgt=0x{item['tgt_addr_linear']:x}")
            lines.append(f"  ref: {item['ref_instr']}")
            lines.append(f"  tgt: {item['tgt_instr']}")
        lines.append("```")
        lines.append("")
    lines.append("Return:")
    lines.append("- a revised C block only")
    lines.append("- a short explanation of why the change should improve code shape")
    return "\n".join(lines).rstrip() + "\n"


def write_snapshot(bundle, snapshot_dir, llm_prompt=False):
    snapshot_root = Path(snapshot_dir)
    snapshot_root.mkdir(parents=True, exist_ok=True)
    stem = f"{bundle['function']}.json"
    payload = dict(bundle)
    payload["snapshot_utc"] = datetime.now(timezone.utc).isoformat()
    path = snapshot_root / stem
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if llm_prompt:
        prompt_path = snapshot_root / f"{bundle['function']}.prompt.txt"
        prompt_path.write_text(build_llm_prompt(bundle), encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description="Build a focused edit bundle for adjusting one C routine toward binary identity.")
    parser.add_argument("--target", choices=["egame", "start"], default="egame")
    parser.add_argument("--function", help="Routine to inspect; defaults to the current top failing routine")
    parser.add_argument("--mzdiff-file", help="Saved mzdiff output path")
    parser.add_argument("--fresh", action="store_true", help="Run the Makefile analyze/verify target first")
    parser.add_argument("--c-radius", type=int, default=8, help="Source lines of C context on each side")
    parser.add_argument("--asm-radius", type=lambda x: int(x, 0), default=0x20, help="Reference asm byte radius")
    parser.add_argument("--cod-radius", type=int, default=3, help="COD source-line radius")
    parser.add_argument("--soft-limit", type=int, default=5, help="Maximum nearby soft diffs to include")
    parser.add_argument("--llm-prompt", action="store_true", help="Render an LLM-ready adjustment prompt instead of the normal report")
    parser.add_argument("--prompt-output", help="Write the LLM prompt to a file")
    parser.add_argument("--snapshot-dir", help="Write the current adjust bundle as JSON into this directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    target_map = "map/egame.map" if args.target == "egame" else "map/start.map"
    lst_file = "lst/egame.lst" if args.target == "egame" else "lst/start.lst"
    mzdiff_file = args.mzdiff_file or ("build/mzdiff_egame.txt" if args.target == "egame" else "build/mzdiff_start.txt")

    if args.fresh:
        make_target = "analyze" if args.target == "egame" else "verify-start"
        rc = run(["make", make_target]).returncode
        if rc != 0:
            raise SystemExit(rc)

    routines = parse_map_file(target_map)
    records, hard_errors_raw, _summary = parse_mzdiff_output(mzdiff_file)
    c_owners = parse_c_functions("src")
    _counts, top_routines = summarize(records, 8)
    hard_errors = enrich_hard_errors(hard_errors_raw, records, routines, c_owners, "src")

    function_name, focus_kind, focus_item = pick_focus(args.function, hard_errors, records, top_routines)
    if not function_name:
        raise SystemExit("No routine found to inspect.")

    cod_path = find_cod_for_function(function_name, c_owners, "src")
    c_file = str(c_owners.get(function_name, [None])[0]) if c_owners.get(function_name) else None
    focus_record = None
    target_relative_offset = None
    reference_offset = None
    cod_line = None
    map_routine = next((item for item in routines if item["name"] == function_name), None)

    if focus_kind == "hard" and focus_item:
        focus_record = focus_item["relevant_record"]
        target_relative_offset = focus_item["target_relative_offset"]
        cod_line = focus_item["cod_line"]
        if focus_record and focus_item.get("map_routine"):
            reference_offset = focus_record["ref_addr_linear"] - focus_item["map_routine"]["begin_linear"]
    elif focus_kind == "soft" and focus_item:
        focus_record = focus_item
        if map_routine and focus_record["routine_tgt_start_linear"] is not None:
            target_relative_offset = focus_record["tgt_addr_linear"] - focus_record["routine_tgt_start_linear"]
            cod_line = find_cod_line(function_name, cod_path, target_relative_offset)
            reference_offset = focus_record["ref_addr_linear"] - map_routine["begin_linear"]

    c_line_num = cod_line["line_num"] if cod_line else None
    c_window = read_source_window(c_file, c_line_num, args.c_radius)
    source_anchor = find_source_anchor(c_file, c_line_num)
    cod_entries = cod_window(cod_path, function_name, c_line_num, args.cod_radius) if cod_path else []
    cod_center_address = None
    if cod_line and cod_line.get("assembly"):
        cod_center_address = cod_line["assembly"][0]["address"]
    anchor_lst_entries = []
    mismatch_lst_entries = []
    if source_anchor:
        anchor_lst_entries = lst_window(lst_file, source_anchor["segment"], source_anchor["offset"], args.asm_radius)
    if map_routine and reference_offset is not None:
        mismatch_lst_entries = lst_window(lst_file, map_routine["segment"], map_routine["begin"] + reference_offset, args.asm_radius)
    best_cod_block_match = find_best_cod_block_match(
        cod_path,
        function_name,
        anchor_lst_entries,
        center_address=cod_center_address,
    )
    local_cod_block_match = find_best_cod_block_match_from_entries(cod_entries, anchor_lst_entries)
    preferred_cod_block_match = local_cod_block_match or best_cod_block_match

    soft_diffs = collect_soft_diffs(records, function_name, args.soft_limit)
    notes = heuristic_notes(focus_kind, focus_item if focus_kind == "hard" else {"relevant_record": focus_record}, soft_diffs)
    notes = add_alignment_notes(notes, source_anchor, map_routine["begin"] + reference_offset if map_routine and reference_offset is not None else None)
    notes = add_block_match_notes(notes, preferred_cod_block_match)
    notes = add_shape_notes(notes, anchor_lst_entries, preferred_cod_block_match)
    notes = add_expression_notes(notes, c_window, cod_entries)

    bundle = {
        "function": function_name,
        "focus_kind": focus_kind,
        "c_file": c_file,
        "cod_path": str(cod_path) if cod_path else None,
        "target_relative_offset": target_relative_offset,
        "reference_offset": reference_offset,
        "source_anchor": source_anchor,
        "focus_record": focus_record,
        "c_window": c_window,
        "cod_window": cod_entries,
        "local_cod_block_match": local_cod_block_match,
        "best_cod_block_match": best_cod_block_match,
        "preferred_cod_block_match": preferred_cod_block_match,
        "anchor_lst_window": anchor_lst_entries,
        "mismatch_lst_window": mismatch_lst_entries,
        "soft_diffs": soft_diffs,
        "notes": notes,
    }

    if args.snapshot_dir:
        write_snapshot(bundle, args.snapshot_dir, llm_prompt=True)

    if args.json:
        print(json.dumps(bundle, indent=2))
        return
    if args.llm_prompt:
        prompt = build_llm_prompt(bundle)
        if args.prompt_output:
            Path(args.prompt_output).write_text(prompt, encoding="utf-8")
        else:
            print(prompt, end="")
        return
    render_report(bundle)


if __name__ == "__main__":
    main()
