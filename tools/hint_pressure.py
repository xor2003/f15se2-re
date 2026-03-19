#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_json(cmd):
    result = subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "command failed")
    return json.loads(result.stdout)


def try_run_json(cmd):
    result = subprocess.run(cmd, cwd=ROOT, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return None, (result.stderr.strip() or result.stdout.strip() or "command failed")
    return json.loads(result.stdout), None


def target_paths(target):
    if target == "start":
        return {
            "map": "map/start.map",
            "conf": "conf/start_rc.json",
            "asm": "src/start_rc.asm",
            "lst": "lst/start.lst",
        }
    return {
        "map": "map/egame.map",
        "conf": "conf/egame_rc.json",
        "asm": "src/egame_rc.asm",
        "lst": "lst/egame.lst",
    }


def build_pressure_report(target, donor_dir):
    paths = target_paths(target)
    catalog = run_json(
        [
            "python3",
            "tools/function_catalog.py",
            "--map",
            paths["map"],
            "--conf",
            paths["conf"],
            "--json",
        ]
    )

    items = []
    ptr_error = None
    donor_error = None
    for entry in catalog:
        if entry.get("status") != "c-owned":
            continue
        name = entry["name"]
        ptr, ptr_err = try_run_json(
            [
                "python3",
                "tools/ptr_hints.py",
                "--target",
                target,
                "--function",
                name,
                "--json",
            ]
        )
        donor, donor_err = try_run_json(
            [
                "python3",
                "tools/donor_search.py",
                "--function",
                name,
                "--donor-dir",
                donor_dir,
                "--asm-source",
                paths["asm"],
                "--lst-source",
                paths["lst"],
                "--map-file",
                paths["map"],
                "--support-symbols",
                "--json",
            ]
        )
        if ptr_err and ptr_error is None:
            ptr_error = ptr_err
        if donor_err and donor_error is None:
            donor_error = donor_err
        ptr_count = len(ptr.get("matched_hints", [])) if ptr else 0
        donor_count = len(donor.get("support_symbols", [])) if donor else 0
        items.append(
            {
                "function": name,
                "ptr_hint_count": ptr_count,
                "donor_hint_count": donor_count,
                "combined_hint_count": ptr_count + donor_count,
                "ptr_error": ptr_err,
                "donor_error": donor_err,
            }
        )

    items.sort(
        key=lambda item: (
            item["combined_hint_count"],
            item["ptr_hint_count"],
            item["donor_hint_count"],
            item["function"],
        ),
        reverse=True,
    )
    return {
        "target": target,
        "donor_dir": donor_dir,
        "ptr_available": ptr_error is None,
        "ptr_error": ptr_error,
        "donor_available": donor_error is None,
        "donor_error": donor_error,
        "functions": items,
    }


def main():
    parser = argparse.ArgumentParser(description="Survey ptr/donor hint pressure across c-owned routines.")
    parser.add_argument("--target", choices=["egame", "start"], default="egame")
    parser.add_argument("--donor-dir", default="/home/xor/games/f14src/src")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_pressure_report(args.target, args.donor_dir)
    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"Hint pressure survey for {report['target']}")
    print(f"Donor dir: {report['donor_dir']}")
    if not report["ptr_available"]:
        print(f"ptr-hints unavailable: {report['ptr_error']}")
    if not report["donor_available"]:
        print(f"donor hints unavailable: {report['donor_error']}")
    for item in report["functions"][: args.top]:
        suffix = ""
        if item["ptr_error"]:
            suffix += " ptr=unavailable"
        if item["donor_error"]:
            suffix += " donor=unavailable"
        print(
            f"- {item['function']}: combined={item['combined_hint_count']} "
            f"ptr={item['ptr_hint_count']} donor={item['donor_hint_count']}{suffix}"
        )


if __name__ == "__main__":
    main()
