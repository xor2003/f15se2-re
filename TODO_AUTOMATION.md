# Automation TODO

## Current Priority

- Detect likely compiler-shape issues automatically:
  - condition compiled with different signedness
  - temporary forcing different evaluation order
  - call/branch drift caused by early control-flow reshaping
- Add a one-command edit loop:
  - rebuild through `make`
  - rerun `mzdiff`
  - refresh the focused adjust bundle
- Review more repo tools and capture the useful ones in workflow docs:
  - `mzsig` for routine signatures
  - `mzdup` for duplicate detection
  - `mzptr` for data-reference discovery

## Later

- Track per-function convergence history in a state file.
- Suggest likely donor snippets based on helper-symbol overlap and local globals.
- Improve block-level similarity scoring beyond mnemonic-only matching.
