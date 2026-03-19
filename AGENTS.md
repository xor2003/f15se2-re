# AGENTS.md

## Project Focus

This repository reconstructs the MS-DOS version of F-15 Strike Eagle II with instruction-level fidelity. The only success metric that matters is whether the rebuilt binaries still match the originals under `mzdiff`.

## Read This First

Start with these root documents:

- `README.md`: overall project goals, binary targets, toolchain, and verification expectations
- `decompile.md`: practical heuristics for turning 16-bit DOS assembly into MSC 5.1-friendly C
- `prompt.txt`: the existing LLM prompt for initial asm-to-C conversion
- `ANALYSIS_GUIDE.md`: notes on `mzretools` analysis internals
- `F15_SE2_REVERSE_ENGINEERING_GUIDE.md`: high-level reconstruction workflow
- `VERIFICATION_DEBUG_GUIDE.md`: debugging and mismatch analysis notes

## Important Directories

- `src/`: reconstructed C, generated headers, and generated assembly stubs
- `conf/`: extraction/replacement configuration for `lst2asm.py` and `lst2ch.py`
- `lst/`: IDA listings and includes
- `map/`: executable maps used by `mzdiff`
- `tools/`: local helper scripts for correlation, naming, and translation
- `mzretools/`: submodule/tool suite used for map generation, diffing, and DOS build helpers
- `UASM/`: assembler submodule
- `/home/xor/games/f14src/src/`: newer donor source tree that may contain exact helper implementations or useful call-site hints, but is not authoritative

## About `mzmap`

`mzmap` is the map-generation and map-inspection frontend in `mzretools`, not part of the normal `make verify-*` loop.

What it does:

- scans a DOS MZ executable and saves an editable `mzretools` map file
- loads and summarizes an existing project map file
- can ingest an IDA `.lst` file and convert it into a `.map` file
- can ingest a Microsoft LINK map and use it to seed routine discovery

What matters for this repo:

- `mzdiff` relies on `map/start.map` and `map/egame.map`
- those map files use the `CodeMap` format emitted by `mzmap`/`CodeMap::save()`
- the map encodes segments, routine extents/chunks, and annotations like `assembly`, `complete`, `external`, and `detached`
- if the map is wrong, `mzdiff`, function ownership, and adjustment tooling can all be misled

Useful source files:

- `mzretools/src/mzmap.cpp`: CLI frontend
- `mzretools/src/codemap.cpp`: actual parsers/savers for IDA listings, linker maps, and `.map`
- `mzretools/include/dos/codemap.h`: `CodeMap` structure
- `mzretools/src/analyzer.cpp`: executable scanning and queue seeding used by `mzmap`

Other `mzretools` binaries worth knowing:

- `mzdiff`: instruction-by-instruction executable comparison with fuzzy matching and target map generation
- `mzsig`: extracts routine signatures from an exe + map, useful for duplicate hunting
- `mzdup`: applies signatures to a target exe/map to find duplicate routines
- `mzptr`: scans an exe + map for data references and variable usage
- `mzhdr`: inspects DOS MZ headers and load-module offsets

Practical findings from local testing:

- `mzptr` and `mzsig` expect an executable that actually matches the provided map file; in this repo that usually means the reference binaries in `bin/`, not the rebuilt outputs in `build/`
- `python3 tools/decomp_workflow.py ptrs --target egame` works as a variable-discovery aid, but its own output warns that variables with more than 1-2 hits are often false positives
- `python3 tools/decomp_workflow.py sigs --target egame --output build/egame.sig --overwrite` works and currently extracts signatures from the reference `egame.exe`
- `mzdup` is useful in principle for duplicate hunting, but on the current `egame` signature set it appears expensive/slow enough that it should be treated as an offline analysis step, not something to run in the tight edit-adjust loop by default
- `mzhdr build/EGAME.EXE -l` reports the load-module offset (`0x200` in the current build), which is helpful when sanity-checking map/exe relationships

## Core Workflow

1. Keep the current baseline valid.
   Run `make verify-egame` or `make verify-start` before and after meaningful changes.
2. Translate one function at a time.
   Remove a routine from generated asm via `conf/egame_rc.json` or `conf/start_rc.json`, then provide the symbol from C.
3. Preserve toolchain fidelity.
   Use the existing MSC 5.1, UASM, and `mzretools` flow; do not replace it with a modern compiler workflow.
4. Let `mzdiff` drive decisions.
   “Equivalent” is not enough if it changes opcode shape or stack layout.

## Build And Verify

- `make egame`: build `EGAME.EXE`
- `make start`: build `start.exe`
- `make verify-egame`: compare rebuilt `EGAME.EXE` against `bin/egame.exe`
- `make verify-start`: compare rebuilt `start.exe` against `bin/start.exe`
- `make analyze`: run `mzdiff` and feed the output into `tools/correlation_analyzer.py`

## Generated Compiler Listings

`.COD` files are generated artifacts from the original Microsoft C 5.1 compiler, invoked through the DOSBox proxy/wrapper path in the `Makefile` and `mzretools/tools/dosbuild.sh`.

Treat them as fresh compiler feedback, not source files:

- edit C
- rebuild through `make`
- let the DOS toolchain regenerate `.COD`
- compare the new `.COD` against the original asm and `mzdiff`

Do not manually maintain `.COD` content.

## Automation Commands

Use these helpers before touching `conf/` by hand:

- `python3 tools/decomp_workflow.py catalog --target egame`
- `python3 tools/decomp_workflow.py verify --target egame`
- `python3 tools/decomp_workflow.py analyze --target egame --fresh`
- `python3 tools/decomp_workflow.py analyze --target egame --function otherKeyDispatch --top 5`
- `python3 tools/decomp_workflow.py adjust --target egame --function otherKeyDispatch`
- `python3 tools/decomp_workflow.py refresh --target egame --function otherKeyDispatch --snapshot-dir /tmp/f15-adjust`
- `python3 tools/decomp_workflow.py ptrs --target egame`
- `python3 tools/decomp_workflow.py sigs --target egame --output build/egame.sig --overwrite`
- `python3 tools/decomp_workflow.py dups build/egame.sig --target egame`
- `python3 tools/decomp_workflow.py iterate --target egame`
- `python3 tools/decomp_workflow.py draft ARCTAN --target egame`
- `python3 tools/donor_search.py --function ARCTAN --donor-dir /home/xor/games/f14src/src`
- `python3 tools/donor_search.py --function otherKeyDispatch --donor-dir /home/xor/games/f14src/src --asm-source src/egame_rc.asm --support-symbols --brief`
- `python3 tools/conf_edit.py show --map map/egame.map --conf conf/egame_rc.json --function ARCTAN`
- `python3 tools/conf_edit.py promote --map map/egame.map --conf conf/egame_rc.json --function ARCTAN --write`

## Practical Loop

There are two common modes:

1. Fix an already C-owned routine.
   Run `python3 tools/decomp_workflow.py iterate --target egame`.
   If the focus routine is `c-owned`, inspect the reported C file, `.COD`, relative offset, and likely C line, then rebuild with `make analyze`.
2. Start a missing routine.
   If `iterate` points at an extracted-only or missing routine, generate a draft, refine it, then promote it into `conf/` with `tools/conf_edit.py`.

The preferred sequence is:

1. `python3 tools/decomp_workflow.py iterate --target egame --fresh`
2. `python3 tools/decomp_workflow.py refresh --target egame --function <routine> --snapshot-dir /tmp/f15-adjust` to rerun the loop and regenerate the current adjustment bundle
3. `python3 tools/decomp_workflow.py adjust --target egame --function <routine>` to inspect the exact C, `.COD`, and original asm window interactively
4. make the smallest possible C adjustment or start a draft for the missing routine
5. `python3 tools/decomp_workflow.py analyze --target egame --function <routine> --top 5`
6. once stable, update `conf/` through `tools/conf_edit.py`
7. rerun `make analyze` or `make verify-egame`

If the donor tree exists, `iterate` and `draft` automatically mine it for exact matches or reference hits. Treat donor code as hint material only:

- exact helper matches like `ARCTAN` are often worth copying/adapting
- gameplay functions may only provide related usage, naming, or structure clues
- never assume donor code is binary-faithful without recompiling and checking `mzdiff`

If a function was already extracted out of `src/egame_rc.asm`, the draft helper falls back to `lst/*.lst` plus `map/*.map` so it can still recover the original asm body for prompting.

Helper-tool usage guidance:

- use `ptrs` when data object naming or pointer replacement is the current bottleneck
- use `sigs` to build a reusable signature file from the reference binary, not from an in-progress rebuilt binary
- use `dups` sparingly, as a side analysis pass for duplicate discovery rather than part of every edit cycle

## Translation Notes

- Favor pre-C89 C style: declare locals at the top of the block.
- Mirror original control flow instead of “cleaning it up”.
- Preserve signedness carefully; `sar` vs `shr`, `jl` vs `jb`, and `idiv` vs `div` often depend on exact types.
- For register-sensitive routines, explicit temporaries sometimes help MSC 5.1 keep values in `si`/`di`.
- Direct array/struct indexing tends to compile more predictably than pointer arithmetic tricks.

## Generated Files

Treat these as generated unless you are intentionally changing the generator inputs:

- `src/egame.h`
- `src/egame_rc.asm`
- `src/start_rc.asm`

Prefer editing:

- `conf/*.json`
- `src/*.c`
- targeted helper scripts in `tools/`

## Git Safety

This repo is often worked in with a dirty tree. Do not reset or discard existing local changes unless explicitly asked. If upstream sync is needed, prefer:

1. fetch and inspect first
2. merge or rebase only after confirming local changes are protected

## LLM Helper

Use `tools/translate_function.py` for an initial asm-to-C draft. It is only a starting point; every translated routine still has to be integrated into the subtractive workflow and verified with `mzdiff`.

If `OPENAI_API_KEY` is not set in the shell, the workflow still works:

- use `tools/decomp_workflow.py draft ...` to print the exact API command you would run
- or paste a draft from your GUI LLM and continue with the normal build/analyze loop
