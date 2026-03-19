# Automation TODO

## Current Priority

- Refine compiler-shape heuristics further:
  - better signed vs unsigned branch detection
  - better temporary/evaluation-order suggestions
  - better call-target drift explanations
  - recognize more low-risk soft-diff patterns beyond mov/global-address drift
  - recognize low-risk same-shaped push/immediate drift around helper calls
  - find or create a real routine case that exercises the push/immediate-drift heuristic
- Review more repo tools and capture the useful ones in workflow docs:
  - keep documenting which `mzretools` outputs are actionable in the tight decompilation loop
  - keep `mzdup` as an offline duplicate-hunting step, not part of the tight edit loop
- Tighten the integrated adjust bundle:
  - keep `ptr-hints` visible in `adjust`/`refresh`
  - collapse or hide lower-priority ptr/donor sections when the bundle gets too large
  - re-run `hint-pressure` as more routines become `c-owned` and retune the display limits when the pressure profile grows
  - test `--full-hints` again once a routine actually exceeds the compact caps
  - re-check `start` pressure once `bin/start.exe` is available for ptr analysis

## Later

- Track per-function convergence history in a state file.
- Suggest likely donor snippets based on helper-symbol overlap and local globals.
- Improve block-level similarity scoring beyond mnemonic-only matching.
