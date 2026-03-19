#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from donor_search import build_donor_report, build_support_symbol_report, render_context_text


DEFAULT_PROMPT = "prompt.txt"
DEFAULT_ASM_SOURCE = "src/egame_rc.asm"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
MAP_ROUTINE_RE = re.compile(r"^([\w_]+):\s+(\w+)\s+(NEAR|FAR)\s+([0-9a-fA-F]+)-([0-9a-fA-F]+)(?:\s+(.*))?$")
LST_LINE_RE = re.compile(r"^(\w+):([0-9a-fA-F]{4})\s+(.*)$")


def load_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def extract_function_from_asm(path, function_name):
    lines = load_text(path).splitlines()
    start = None
    end = None
    names = [function_name, f"_{function_name}"]

    for index, line in enumerate(lines):
        stripped = line.strip()
        lowered = stripped.lower()
        for name in names:
            if lowered.startswith(f"{name.lower()} proc"):
                start = index
                break
        if start is not None:
            break

    if start is None:
        raise ValueError(f"Could not find function '{function_name}' in {path}")

    for index in range(start + 1, len(lines)):
        lowered = lines[index].strip().lower()
        for name in names:
            if lowered == f"{name.lower()} endp":
                end = index
                break
        if end is not None:
            break

    if end is None:
        raise ValueError(f"Could not find matching endp for '{function_name}' in {path}")

    return "\n".join(lines[start : end + 1]).strip() + "\n"


def parse_map_routine(path, function_name):
    for raw_line in load_text(path).splitlines():
        line = raw_line.strip()
        match = MAP_ROUTINE_RE.match(line)
        if not match or match.group(1) != function_name:
            continue
        return {
            "name": match.group(1),
            "segment": match.group(2),
            "begin": int(match.group(4), 16),
            "end": int(match.group(5), 16),
        }
    raise ValueError(f"Could not find function '{function_name}' in {path}")


def extract_function_from_lst(lst_path, map_path, function_name):
    routine = parse_map_routine(map_path, function_name)
    lines = []
    for raw_line in load_text(lst_path).splitlines():
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
        raise ValueError(f"Could not extract function '{function_name}' from {lst_path}")
    return "\n".join(lines).strip() + "\n"


def extract_function_text(function_name, asm_source, lst_source=None, map_file=None):
    try:
        return extract_function_from_asm(asm_source, function_name)
    except ValueError:
        if lst_source and map_file:
            return extract_function_from_lst(lst_source, map_file, function_name)
        raise


def build_user_prompt(args, asm_text):
    context_chunks = []
    for context_path in args.context:
        context_text = load_text(context_path).strip()
        context_chunks.append(
            f"Context file: {context_path}\n"
            f"```text\n{context_text}\n```"
        )

    target_name = args.function or os.path.basename(args.asm_file or "stdin")
    if args.donor_dir and args.function:
        donor_report = build_donor_report(args.function, args.donor_dir, max_refs=args.donor_max_refs)
        if donor_report["exact_matches"] or donor_report["reference_hits"]:
            context_chunks.append(render_context_text(donor_report).strip())
        if args.asm_source:
            support_report = build_support_symbol_report(
                args.function,
                args.asm_source,
                args.donor_dir,
                max_symbols=args.donor_max_symbols,
                max_refs=min(args.donor_max_refs, 4),
                lst_source=args.lst_source,
                map_file=args.map_file,
            )
            if support_report["support_symbols"]:
                support_lines = ["Supporting donor hints from called asm symbols:"]
                for item in support_report["support_symbols"]:
                    if item["best_exact_match"]:
                        match = item["best_exact_match"]
                        support_lines.append(
                            f"- {item['symbol']}: exact donor match in {match['relative_path']}:{match['start_line']}"
                        )
                    elif item["best_reference_hit"]:
                        hit = item["best_reference_hit"]
                        support_lines.append(
                            f"- {item['symbol']}: donor reference in {hit['relative_path']}:{hit['line']}"
                        )
                context_chunks.append("\n".join(support_lines))

    instructions = textwrap.dedent(
        f"""
        Produce an initial C translation draft for the following 16-bit DOS assembly routine.

        Requirements:
        - Target the project's existing MSC 5.1 style and constraints.
        - Keep the output pre-C89 compatible.
        - Prefer readable but compiler-faithful C over aggressive cleanup.
        - Point out uncertainties, guessed types, and places that may need verification with mzdiff.
        - Return plain text only.
        - Start with a C code block.
        - After the code block, include a short "Notes:" section.

        Routine name: {target_name}
        """
    ).strip()

    parts = [instructions]
    if context_chunks:
        parts.append("\n\n".join(context_chunks))
    parts.append(f"Assembly input:\n```asm\n{asm_text.rstrip()}\n```")
    return "\n\n".join(parts)


def call_responses_api(base_url, api_key, model, system_prompt, user_prompt, effort):
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_prompt}],
            },
        ],
    }
    if effort:
        payload["reasoning"] = {"effort": effort}

    return post_json(f"{base_url.rstrip('/')}/responses", api_key, payload)


def call_chat_api(base_url, api_key, model, system_prompt, user_prompt):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    return post_json(f"{base_url.rstrip('/')}/chat/completions", api_key, payload)


def post_json(url, api_key, payload):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API request failed with HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"API request failed: {exc}") from exc


def extract_text(response_json):
    if isinstance(response_json.get("output_text"), str) and response_json["output_text"].strip():
        return response_json["output_text"]

    choices = response_json.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        parts.append(text)
            if parts:
                return "\n".join(parts)

    output = response_json.get("output")
    if isinstance(output, list):
        parts = []
        for item in output:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if not isinstance(content, dict):
                    continue
                text = content.get("text")
                if text:
                    parts.append(text)
            if parts:
                return "\n".join(parts)

    raise RuntimeError("Could not extract model text from API response")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate an initial asm-to-C draft for a function using an OpenAI or OpenAI-compatible API."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--asm-file", help="Assembly file to send as-is")
    source.add_argument("--function", help=f"Function name to extract from {DEFAULT_ASM_SOURCE} or --asm-source")
    source.add_argument("--stdin", action="store_true", help="Read assembly input from stdin")

    parser.add_argument(
        "--asm-source",
        default=DEFAULT_ASM_SOURCE,
        help="Assembly source used with --function (default: %(default)s)",
    )
    parser.add_argument(
        "--lst-source",
        help="IDA listing fallback used when a function is not present in --asm-source",
    )
    parser.add_argument(
        "--map-file",
        help="Map file used together with --lst-source to bound function extraction",
    )
    parser.add_argument(
        "--prompt-file",
        default=DEFAULT_PROMPT,
        help="Base system prompt file (default: %(default)s)",
    )
    parser.add_argument(
        "--context",
        action="append",
        default=["decompile.md"],
        help="Extra context file to include; may be passed multiple times",
    )
    parser.add_argument(
        "--donor-dir",
        help="Optional donor source tree to mine for exact or nearby matches",
    )
    parser.add_argument(
        "--donor-max-refs",
        type=int,
        default=8,
        help="Maximum donor reference hits to include (default: %(default)s)",
    )
    parser.add_argument(
        "--donor-max-symbols",
        type=int,
        default=6,
        help="Maximum called helper symbols to inspect in donor sources (default: %(default)s)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
        help="Model name (default: OPENAI_MODEL or %(default)s)",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
        help="API base URL (default: OPENAI_BASE_URL or %(default)s)",
    )
    parser.add_argument(
        "--api",
        choices=["responses", "chat"],
        default=os.environ.get("OPENAI_API_MODE", "responses"),
        help="API style to use (default: OPENAI_API_MODE or %(default)s)",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=["low", "medium", "high"],
        default=os.environ.get("OPENAI_REASONING_EFFORT"),
        help="Responses API reasoning effort",
    )
    parser.add_argument(
        "--output",
        help="Write model output to a file instead of stdout",
    )
    parser.add_argument(
        "--print-request",
        action="store_true",
        help="Print the fully composed user prompt to stderr before sending",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is required", file=sys.stderr)
        return 2

    if args.stdin:
        asm_text = sys.stdin.read()
    elif args.asm_file:
        asm_text = load_text(args.asm_file)
    else:
        asm_text = extract_function_text(args.function, args.asm_source, args.lst_source, args.map_file)

    system_prompt = load_text(args.prompt_file).strip()
    user_prompt = build_user_prompt(args, asm_text)

    if args.print_request:
        print(user_prompt, file=sys.stderr)

    if args.api == "responses":
        response_json = call_responses_api(
            args.base_url,
            api_key,
            args.model,
            system_prompt,
            user_prompt,
            args.reasoning_effort,
        )
    else:
        response_json = call_chat_api(
            args.base_url,
            api_key,
            args.model,
            system_prompt,
            user_prompt,
        )

    text = extract_text(response_json).rstrip() + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
