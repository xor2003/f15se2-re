# Automation TODO

## Current Priority

- Refine compiler-shape heuristics further:
  - better signed vs unsigned branch detection
  - better temporary/evaluation-order suggestions
  - better call-target drift explanations
- Feed `ptr-hints` into the normal adjust loop:
  - show matched globals alongside `adjust`/`refresh` bundles
  - use `mzptr` as a naming/pointer-offset aid, not as a code-reference tracer
- Review more repo tools and capture the useful ones in workflow docs:
  - keep documenting which `mzretools` outputs are actionable in the tight decompilation loop
  - keep `mzdup` as an offline duplicate-hunting step, not part of the tight edit loop

## Later

- Track per-function convergence history in a state file.
- Suggest likely donor snippets based on helper-symbol overlap and local globals.
- Improve block-level similarity scoring beyond mnemonic-only matching.
