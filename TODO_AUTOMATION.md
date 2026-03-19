# Automation TODO

## Current Priority

- Refine compiler-shape heuristics further:
  - better signed vs unsigned branch detection
  - better temporary/evaluation-order suggestions
  - better call-target drift explanations
- Review more repo tools and capture the useful ones in workflow docs:
  - keep documenting which `mzretools` outputs are actionable in the tight decompilation loop
  - keep `mzdup` as an offline duplicate-hunting step, not part of the tight edit loop
- Tighten the integrated adjust bundle:
  - keep `ptr-hints` visible in `adjust`/`refresh`
  - trim noisy hints when a routine touches many globals
  - trim noisy donor support when the asm routine calls many helpers
  - collapse or hide lower-priority ptr/donor sections when the bundle gets too large

## Later

- Track per-function convergence history in a state file.
- Suggest likely donor snippets based on helper-symbol overlap and local globals.
- Improve block-level similarity scoring beyond mnemonic-only matching.
