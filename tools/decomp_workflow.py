#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DONOR_DIR = "/home/xor/games/f14src/src"


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, check=False)


def run_capture(cmd):
    return subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)


def default_donor_dir():
    return DEFAULT_DONOR_DIR if Path(DEFAULT_DONOR_DIR).exists() else None


def guess_target(function_name):
    if function_name[0].islower():
        return "egame"
    return "egame"


def main():
    parser = argparse.ArgumentParser(description="Small orchestrator for the F-15 SE2 decompilation workflow.")
    sub = parser.add_subparsers(dest="command", required=True)

    catalog = sub.add_parser("catalog")
    catalog.add_argument("--target", choices=["egame", "start"], default="egame")
    catalog.add_argument("--json", action="store_true")

    promote = sub.add_parser("promote")
    promote.add_argument("function")
    promote.add_argument("--target", choices=["egame", "start"], default="egame")
    promote.add_argument("--write", action="store_true")

    demote = sub.add_parser("demote")
    demote.add_argument("function")
    demote.add_argument("--target", choices=["egame", "start"], default="egame")
    demote.add_argument("--write", action="store_true")

    draft = sub.add_parser("draft")
    draft.add_argument("function")
    draft.add_argument("--target", choices=["egame", "start"], default="egame")
    draft.add_argument("--asm-source", default="src/egame_rc.asm")
    draft.add_argument("--output")
    draft.add_argument("--donor-dir", default=default_donor_dir())

    analyze = sub.add_parser("analyze")
    analyze.add_argument("--target", choices=["egame", "start"], default="egame")
    analyze.add_argument("--mzdiff-file")
    analyze.add_argument("--function")
    analyze.add_argument("--top", type=int, default=8)
    analyze.add_argument("--fresh", action="store_true", help="Run the Makefile analyze/verify target first")
    analyze.add_argument("--donor-dir", default=default_donor_dir())

    adjust = sub.add_parser("adjust")
    adjust.add_argument("--target", choices=["egame", "start"], default="egame")
    adjust.add_argument("--function")
    adjust.add_argument("--fresh", action="store_true", help="Run the Makefile analyze/verify target first")
    adjust.add_argument("--llm-prompt", action="store_true")
    adjust.add_argument("--prompt-output")
    adjust.add_argument("--snapshot-dir")
    adjust.add_argument("--json", action="store_true")

    verify = sub.add_parser("verify")
    verify.add_argument("--target", choices=["egame", "start", "all"], default="egame")

    iterate = sub.add_parser("iterate")
    iterate.add_argument("--target", choices=["egame", "start"], default="egame")
    iterate.add_argument("--fresh", action="store_true", help="Run the Makefile analyze/verify target first")
    iterate.add_argument("--draft-missing", action="store_true", help="Attempt to generate a draft for a missing routine")
    iterate.add_argument("--draft-output", help="Draft output path when --draft-missing is used")
    iterate.add_argument("--donor-dir", default=default_donor_dir())

    args = parser.parse_args()

    target_map = f"map/{args.target}.map" if args.target == "start" else "map/egame.map"
    target_conf = f"conf/{args.target}_rc.json" if args.target == "start" else "conf/egame_rc.json"

    if args.command == "catalog":
        cmd = [sys.executable, "tools/function_catalog.py", "--map", target_map, "--conf", target_conf]
        if args.json:
            cmd.append("--json")
        raise SystemExit(run(cmd).returncode)

    if args.command in {"promote", "demote"}:
        cmd = [
            sys.executable,
            "tools/conf_edit.py",
            args.command,
            "--map",
            target_map,
            "--conf",
            target_conf,
            "--function",
            args.function,
        ]
        if args.write:
            cmd.append("--write")
        raise SystemExit(run(cmd).returncode)

    if args.command == "draft":
        cmd = [sys.executable, "tools/translate_function.py", "--function", args.function, "--asm-source", args.asm_source]
        if args.target == "egame":
            cmd.extend(["--lst-source", "lst/egame.lst", "--map-file", "map/egame.map"])
        else:
            cmd.extend(["--lst-source", "lst/start.lst", "--map-file", "map/start.map"])
        if args.output:
            cmd.extend(["--output", args.output])
        if args.donor_dir:
            cmd.extend(["--donor-dir", args.donor_dir])
        if "OPENAI_API_KEY" not in os.environ:
            print("OPENAI_API_KEY is not set; use this command once the key is available:")
            print(" ".join(cmd))
            return
        raise SystemExit(run(cmd).returncode)

    if args.command == "analyze":
        if args.fresh:
            make_target = "analyze" if args.target == "egame" else "verify-start"
            rc = run(["make", make_target]).returncode
            if rc != 0:
                raise SystemExit(rc)
        mzdiff_file = args.mzdiff_file or ("build/mzdiff_egame.txt" if args.target == "egame" else "build/mzdiff_start.txt")
        lst_file = "lst/egame.lst" if args.target == "egame" else "lst/start.lst"
        cmd = [
            sys.executable,
            "tools/correlation_analyzer.py",
            mzdiff_file,
            "--map-file",
            target_map,
            "--lst-file",
            lst_file,
            "--src-dir",
            "src",
            "--top",
            str(args.top),
        ]
        if args.function:
            cmd.extend(["--function", args.function])
        rc = run(cmd).returncode
        if rc != 0:
            raise SystemExit(rc)
        if args.function and args.donor_dir:
            donor = run(
                [
                    sys.executable,
                    "tools/donor_search.py",
                    "--function",
                    args.function,
                    "--donor-dir",
                    args.donor_dir,
                    "--brief",
                ]
            ).returncode
            if donor != 0:
                raise SystemExit(donor)
            support = run(
                [
                    sys.executable,
                    "tools/donor_search.py",
                    "--function",
                    args.function,
                    "--donor-dir",
                    args.donor_dir,
                    "--asm-source",
                    "src/egame_rc.asm" if args.target == "egame" else "src/start_rc.asm",
                    "--lst-source",
                    "lst/egame.lst" if args.target == "egame" else "lst/start.lst",
                    "--map-file",
                    target_map,
                    "--support-symbols",
                    "--brief",
                ]
            ).returncode
            if support != 0:
                raise SystemExit(support)
        raise SystemExit(0)

    if args.command == "adjust":
        cmd = [sys.executable, "tools/adjust_function.py", "--target", args.target]
        if args.function:
            cmd.extend(["--function", args.function])
        if args.fresh:
            cmd.append("--fresh")
        if args.llm_prompt:
            cmd.append("--llm-prompt")
        if args.prompt_output:
            cmd.extend(["--prompt-output", args.prompt_output])
        if args.snapshot_dir:
            cmd.extend(["--snapshot-dir", args.snapshot_dir])
        if args.json:
            cmd.append("--json")
        raise SystemExit(run(cmd).returncode)

    if args.command == "verify":
        if args.target == "all":
            raise SystemExit(run(["make", "verify"]).returncode)
        target = "verify-egame" if args.target == "egame" else "verify-start"
        raise SystemExit(run(["make", target]).returncode)

    if args.command == "iterate":
        if args.fresh:
            make_target = "analyze" if args.target == "egame" else "verify-start"
            rc = run(["make", make_target]).returncode
            if rc != 0:
                raise SystemExit(rc)

        mzdiff_file = "build/mzdiff_egame.txt" if args.target == "egame" else "build/mzdiff_start.txt"
        lst_file = "lst/egame.lst" if args.target == "egame" else "lst/start.lst"

        analysis = run_capture(
            [
                sys.executable,
                "tools/correlation_analyzer.py",
                mzdiff_file,
                "--map-file",
                target_map,
                "--lst-file",
                lst_file,
                "--src-dir",
                "src",
                "--json",
            ]
        )
        if analysis.returncode != 0:
            sys.stderr.write(analysis.stderr)
            raise SystemExit(analysis.returncode)
        analysis_json = json.loads(analysis.stdout)

        focus = None
        mode = None
        if analysis_json.get("hard_errors"):
            focus = analysis_json["hard_errors"][0]["routine"]
            mode = "fix"
        elif analysis_json.get("summary", {}).get("first_mismatch", {}).get("routine"):
            focus = analysis_json["summary"]["first_mismatch"]["routine"]
            mode = "start"
        elif analysis_json.get("top_routines"):
            focus = analysis_json["top_routines"][0][0]
            mode = "inspect"

        if not focus:
            print("No focus routine found.")
            raise SystemExit(0)

        catalog = run_capture(
            [
                sys.executable,
                "tools/function_catalog.py",
                "--map",
                target_map,
                "--conf",
                target_conf,
                "--name",
                focus,
                "--json",
            ]
        )
        if catalog.returncode != 0:
            sys.stderr.write(catalog.stderr)
            raise SystemExit(catalog.returncode)
        catalog_json = json.loads(catalog.stdout)
        catalog_item = catalog_json[0] if catalog_json else None

        print(f"Focus routine: {focus}")
        print(f"Mode: {mode}")
        if catalog_item:
            print(f"Status: {catalog_item['status']}")
            if catalog_item.get("c_files"):
                print(f"C files: {', '.join(catalog_item['c_files'])}")

        if args.donor_dir:
            donor = run_capture(
                [
                    sys.executable,
                    "tools/donor_search.py",
                    "--function",
                    focus,
                    "--donor-dir",
                    args.donor_dir,
                    "--brief",
                ]
            )
            if donor.returncode == 0 and donor.stdout.strip():
                print(donor.stdout.strip())
            support = run_capture(
                [
                    sys.executable,
                    "tools/donor_search.py",
                    "--function",
                    focus,
                    "--donor-dir",
                    args.donor_dir,
                    "--asm-source",
                    "src/egame_rc.asm" if args.target == "egame" else "src/start_rc.asm",
                    "--lst-source",
                    "lst/egame.lst" if args.target == "egame" else "lst/start.lst",
                    "--map-file",
                    target_map,
                    "--support-symbols",
                    "--brief",
                ]
            )
            if support.returncode == 0 and support.stdout.strip():
                print(support.stdout.strip())

        if mode == "fix":
            hard = analysis_json["hard_errors"][0]
            if hard.get("cod_path"):
                print(f"COD: {hard['cod_path']}")
            if hard.get("target_relative_offset") is not None:
                print(f"Target relative offset: 0x{hard['target_relative_offset']:x}")
            cod_line = hard.get("cod_line")
            if cod_line:
                print(f"Likely C line: {cod_line['line_num']}: {cod_line['c_code']}")
            print("Next:")
            print(f"  python3 tools/decomp_workflow.py analyze --target {args.target} --function {focus} --top 5")
        elif mode == "start":
            print("Next:")
            print(f"  python3 tools/function_catalog.py --map {target_map} --conf {target_conf} --name {focus} --json")
            print(f"  python3 tools/decomp_workflow.py draft {focus} --target {args.target}")
            print(f"  python3 tools/conf_edit.py promote --map {target_map} --conf {target_conf} --function {focus}")
            if args.draft_missing:
                draft_cmd = [
                    sys.executable,
                    "tools/translate_function.py",
                    "--function",
                    focus,
                    "--asm-source",
                    "src/egame_rc.asm" if args.target == "egame" else "src/start_rc.asm",
                    "--lst-source",
                    "lst/egame.lst" if args.target == "egame" else "lst/start.lst",
                    "--map-file",
                    target_map,
                ]
                if args.donor_dir:
                    draft_cmd.extend(["--donor-dir", args.donor_dir])
                if args.draft_output:
                    draft_cmd.extend(["--output", args.draft_output])
                if "OPENAI_API_KEY" in os.environ:
                    rc = run(draft_cmd).returncode
                    if rc != 0:
                        raise SystemExit(rc)
                else:
                    print("OPENAI_API_KEY is not set; draft command:")
                    print("  " + " ".join(draft_cmd))
        else:
            print(f"  python3 tools/decomp_workflow.py analyze --target {args.target} --function {focus} --top 5")
        raise SystemExit(0)


if __name__ == "__main__":
    main()
