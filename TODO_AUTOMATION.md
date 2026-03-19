# Automation TODO

## Current Priority

- Refine compiler-shape heuristics further:
  - better signed vs unsigned branch detection
  - better temporary/evaluation-order suggestions
  - better call-target drift explanations
  - recognize more low-risk soft-diff patterns beyond mov/global-address drift
  - recognize low-risk same-shaped push/immediate drift around helper calls
  - recognize low-risk same-shaped stack-slot drift around helper setup and temporary reuse
  - keep widening the soft-only pattern library from real cases like paired AX/DX split-copy drift
  - if generic store-fanout routines like `InitializeGameSettings` need extra help, add a separate heuristic for that shape instead of broadening the AX/DX split-copy trigger
  - keep validating new soft-only heuristics against at least one positive routine and two negative control routines before committing them
  - keep checking early prologue drift separately from later block drift, because stack-frame size mismatches are often a local-count issue, not a control-flow issue
  - keep enough nearby soft diffs in the default adjust bundle to let later early-block patterns appear; current default `soft-limit=8` is now intentional
  - treat repeated far-pointer reloads separately from generic call drift, because `les bx, [...]` sequences often mean the same far data walk with shifted storage
  - treat repeated helper-call setup blocks separately from generic push drift, because stable `push/push/call` rhythm often means the call shape still matches even when symbols move
  - treat repeated literal-load/jump-tail blocks separately from generic branch drift, because case/error dispatch code often keeps the same shared tail while labels and literals slide
  - use `UpdateFlightModelAndHUD` as a near-case and find or create a cleaner routine that exercises the push/immediate-drift heuristic directly
  - use `UpdateFlightModelAndHUD` as the current near-case for stack-slot drift too, unless a cleaner early-window trigger appears
- Keep toolkit tests in lockstep with behavior:
  - extend `tests/test_toolkit_heuristics.py` whenever a new heuristic or guard is added
  - keep one positive and at least two negative/control cases for each new soft-only heuristic
  - add CLI-level smoke tests for `adjust`/`analyze` output shaping if the Python toolkit grows more complex
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
