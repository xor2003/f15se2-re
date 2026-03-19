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
- `mzptr` is not a code xref tracer for the current routine; it reports executable locations where variable offsets appear to be stored, so it is most useful for pointer/naming cleanup rather than direct asm-to-C control-flow matching
- `python3 tools/decomp_workflow.py sigs --target egame --output build/egame.sig --overwrite` works and currently extracts signatures from the reference `egame.exe`
- `mzdup` is useful in principle for duplicate hunting, but on the current `egame` signature set it appears expensive/slow enough that it should be treated as an offline analysis step, not something to run in the tight edit-adjust loop by default
- `mzhdr build/EGAME.EXE -l` reports the load-module offset (`0x200` in the current build), which is helpful when sanity-checking map/exe relationships
- `python3 tools/decomp_workflow.py ptr-hints <function> --target egame` is now the practical `mzptr` entrypoint: it maps `mzptr` variables back onto named globals used by the target C routine by combining `map/egame.map`, `lst/egame.lst`, and `egame_rc.lst`
- in current local testing, `ptr-hints` produces useful matches for already converted routines such as `ProcessPlayerInputAndAI`, `UpdateFlightModelAndHUD`, and `otherKeyDispatch`, with an inferred `egame_rc.lst` BSS-to-map shift of `0x66c0`

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
- `python3 -m unittest tests/test_toolkit_heuristics.py`: run the Python regression tests for toolkit heuristics before and after changing `tools/adjust_function.py`
- `python3 -m py_compile tools/adjust_function.py tools/decomp_workflow.py tools/correlation_analyzer.py tools/ptr_hints.py tools/donor_search.py tools/hint_pressure.py`: quick syntax smoke test for the current Python toolkit
- `python3 tools/decomp_workflow.py adjust --target egame --function <name>` now defaults to a slightly wider nearby soft-diff window (`8` entries), which is important for later early-block patterns like repeated far-pointer reloads

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
- `python3 tools/decomp_workflow.py ptr-hints ProcessPlayerInputAndAI --target egame`
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

Findings from trying the toolkit on already converted functions:

- `otherKeyDispatch` is a good hard-mismatch test case for the full `refresh`/`adjust` loop
- `ProcessPlayerInputAndAI` and `UpdateFlightModelAndHUD` are useful soft-diff test cases for already C-owned routines
- function-scoped `analyze --function ...` should suppress unrelated hard mismatches from other routines, otherwise the output is misleading
- for soft-diff routines, the most useful `.COD` block match is usually the local match near the current `.COD` window, not the best match anywhere in the whole function
- `adjust` now includes `ptr-hints` inline, which makes the main edit bundle more useful for routines that already touch named globals and pointer-like data objects
- the inline `ptr-hints` list is now ranked by the current C edit window first; for example, `UpdateFlightModelAndHUD` correctly bubbles `word_330C2` to the top because it appears inside the active mismatch window
- `adjust` now also carries donor hints inline: exact donor matches when they exist, plus helper-symbol hits when the routine itself has no direct donor twin. In current testing this surfaces `ARCTAN` for `UpdateFlightModelAndHUD` and `kbhit`/`bios_keybrd` support for `otherKeyDispatch`
- donor support hints are now ranked by the active C window too, so helpers already visible in the mismatch region, like `ARCTAN` in `UpdateFlightModelAndHUD`, are explicitly called out as local hints instead of being buried in generic support output
- when a donor helper is both local and has an exact body available, `adjust` now inlines the top donor snippet directly into the bundle. In current testing this pulls in the `ARCTAN` body from `MATH.ASM` for `UpdateFlightModelAndHUD`, while routines with only loose helper references stay compact
- long donor snippets are now summarized to a bounded head/tail view inside `adjust`, so large helper bodies stay visible without drowning out the current mismatch window
- the human-facing `adjust` report and `--llm-prompt` view now cap lower-priority ptr/donor entries while keeping the ranked full lists in the bundle data, so readability improves without throwing away machine-usable context
- `adjust --full-hints` now disables that compact display cap for explicit deep dives; in current testing on the existing sample routines the visible output stays the same because their ranked hint sets are already under the compact thresholds
- `python3 tools/decomp_workflow.py hint-pressure --target egame` now surveys ptr/donor hint counts across all `c-owned` routines. In the current `egame` state, the noisiest routines are `ProcessPlayerInputAndAI` (6 combined hints), `otherKeyDispatch` (5), and `UpdateFlightModelAndHUD` (4), which means the present compact-display caps are not yet being stressed by the shipped sample set
- `hint-pressure` now degrades gracefully when ptr hints are unavailable for a target. In the current `start` state, `bin/start.exe` is missing, so ptr pressure cannot be measured there yet; donor pressure across current `c-owned` `start` routines is effectively zero
- the adjust heuristics now call out low-risk prologue/global-address drift patterns in soft-diff routines. In current testing this helps `ProcessPlayerInputAndAI` read as mostly `mov`/operand-address drift instead of falsely suggesting a major control-flow mismatch
- the soft-diff notes now also recognize repeated AX/DX copy drift in early `mov` blocks. In current testing this helps `ProcessPlayerInputAndAI` read as a likely 32-bit global copy or split-store block with symbol/layout drift, instead of implying that the surrounding C structure is already badly wrong. The trigger is now intentionally narrow: it stays out of generic store-fanout routines like `InitializeGameSettings`
- the soft-diff notes now also recognize one-value fan-out store blocks. In current testing this helps `InitializeGameSettings` read as a likely “load one setting, then splash it into several globals” block with layout drift, while staying out of `ProcessPlayerInputAndAI` and `UpdateFlightModelAndHUD`
- the soft-diff notes now also recognize prologue stack-frame size drift. In current testing this helps `main` read as a local/temp-footprint mismatch (`sub sp, 0x6` vs `0x4`) instead of prematurely implying broken control flow
- the soft-diff notes now also recognize repeated far-pointer reloads. In current testing this helps `main` read as repeated access to the same far struct/overlay base (`les bx, [...]`) with layout drift, instead of implying that the repeated helper-call sequence is already structurally wrong
- the soft-diff notes now also recognize repeated helper-call setup blocks with matching `push`/`call` shape. In current testing this helps `moveNearFar` read as stable argument staging around `movedata`, with symbol/storage drift rather than a broken call sequence
- the soft-diff notes now also recognize repeated literal-load plus jump-to-shared-tail blocks. In current testing this helps `openFile` read as a stable case/error-selection shape where literal addresses and shared-tail placement drift, rather than a fundamentally different branch structure
- the soft-diff notes now also recognize repeated constant table/register setup. In current testing this helps `setupDac` read as staging of the same palette/table pointers with shifted table addresses, rather than as a random cluster of unrelated immediate loads
- the soft-diff notes now also recognize repeated bare helper-call drift without much surrounding argument setup. In current testing this helps `gfxInit` read as repeated aligned helper call sites with thunk/overlay address drift, while staying out of push-heavy call setup cases like `drawSomeStrings`
- the soft-diff notes now also recognize callback/vector install setup drift. In current testing this helps `setTimerIrqHanlder` read as capturing the same far handler pointers into different slots/vectors, instead of looking like an arbitrary mix of stores and far loads
- the soft-diff notes now also distinguish same-shaped `call` target drift from local control-flow breakage. In current testing this helps `UpdateFlightModelAndHUD` read as possible helper/thunk address drift rather than immediate evidence that the surrounding C structure is wrong
- a same-shaped `push`-setup drift recognizer is now wired into the soft-diff notes too. The current sample set still does not trigger it as a primary note, but `UpdateFlightModelAndHUD` shows a near-case with early `push [bp-..]` drift around the `ARCTAN` call setup, which is a good future validation target
- a same-shaped stack-slot drift recognizer is also wired into the soft-diff notes now. It looks for repeated early `[bp-..]` operand drift on the same instruction shape, which should help separate local temporary-slot churn from real control-flow damage. In the current `egame` sample set it still behaves as a guarded near-case rather than a primary trigger; `UpdateFlightModelAndHUD` remains the best validation target because its early diffs include local slot churn around the `ARCTAN` setup, but not densely enough yet to trip the note
- `tests/test_toolkit_heuristics.py` now regression-tests the current heuristic set, including positive and negative controls for paired `AX/DX` drift, fan-out store drift, prologue stack-frame drift, repeated far-pointer reload drift, repeated helper-call setup drift, repeated literal-load/jump-tail drift, repeated constant table/register setup drift, repeated bare helper-call drift, callback/vector install drift, and same-shaped call-target drift. Keep it updated when changing `heuristic_notes()`
- the current planning backlog now explicitly tracks 20 next heuristic candidates in `TODO_AUTOMATION.md`; use that backlog to choose the next real pattern to implement instead of inventing a fresh direction each time

If the donor tree exists, `iterate` and `draft` automatically mine it for exact matches or reference hits. Treat donor code as hint material only:

- exact helper matches like `ARCTAN` are often worth copying/adapting
- gameplay functions may only provide related usage, naming, or structure clues
- never assume donor code is binary-faithful without recompiling and checking `mzdiff`

If a function was already extracted out of `src/egame_rc.asm`, the draft helper falls back to `lst/*.lst` plus `map/*.map` so it can still recover the original asm body for prompting.

Helper-tool usage guidance:

- use `ptrs` when data object naming or pointer replacement is the current bottleneck
- use `ptr-hints <function>` when a specific C-owned routine needs a filtered view of `mzptr` hints for globals already referenced by that routine
- expect the same `ptr-hints` data to show up inside `adjust` and `refresh` bundles now; use it as supporting evidence when deciding whether a hardcoded offset should become a named global/pointer expression
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
