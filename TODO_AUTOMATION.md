# Automation TODO

## Current Priority

- Refine compiler-shape heuristics further:
  - better signed vs unsigned branch detection
  - better temporary/evaluation-order suggestions
  - better call-target drift explanations
- Review more repo tools and capture the useful ones in workflow docs:
  - follow up on `mzptr` as the most promising helper for local/global naming support
  - keep `mzdup` as an offline duplicate-hunting step, not part of the tight edit loop

## Later

- Track per-function convergence history in a state file.
- Suggest likely donor snippets based on helper-symbol overlap and local globals.
- Improve block-level similarity scoring beyond mnemonic-only matching.
