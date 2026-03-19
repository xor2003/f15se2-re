# Automation TODO

## Current Priority

- Refine compiler-shape heuristics further:
  - better signed vs unsigned branch detection
  - better temporary/evaluation-order suggestions
  - better call-target drift explanations
- Review more repo tools and capture the useful ones in workflow docs:
  - `mzsig` for routine signatures
  - `mzdup` for duplicate detection
  - `mzptr` for data-reference discovery

## Later

- Track per-function convergence history in a state file.
- Suggest likely donor snippets based on helper-symbol overlap and local globals.
- Improve block-level similarity scoring beyond mnemonic-only matching.
