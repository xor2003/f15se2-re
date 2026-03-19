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
    for entry in catalog:
        if entry.get("status") != "c-owned":
            continue
        name = entry["name"]
        ptr = run_json(
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
        donor = run_json(
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
        ptr_count = len(ptr.get("matched_hints", []))
        donor_count = len(donor.get("support_symbols", []))
        items.append(
            {
                "function": name,
                "ptr_hint_count": ptr_count,
                "donor_hint_count": donor_count,
                "combined_hint_count": ptr_count + donor_count,
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
    for item in report["functions"][: args.top]:
        print(
            f"- {item['function']}: combined={item['combined_hint_count']} "
            f"ptr={item['ptr_hint_count']} donor={item['donor_hint_count']}"
        )


if __name__ == "__main__":
    main()
