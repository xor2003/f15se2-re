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
  - treat repeated constant table/register setup separately from generic immediate drift, because palette/table-heavy code often stages the same pointer roles with different base addresses
  - treat repeated bare helper-call drift separately from push-heavy setup drift, because some routines like `gfxInit` repeat the same helper calls with very little argument staging
  - use `UpdateFlightModelAndHUD` as a near-case and find or create a cleaner routine that exercises the push/immediate-drift heuristic directly
  - use `UpdateFlightModelAndHUD` as the current near-case for stack-slot drift too, unless a cleaner early-window trigger appears
- Next 20 heuristic candidates, ordered as a working backlog:
  - signed-vs-unsigned branch drift: recognize `jl/jg`-style vs `jb/ja`-style comparison shape when only operand types drift
  - zero-vs-nonzero branch materialization drift: detect `cmp/test + jz/jnz` blocks that keep the same condition role while labels move
  - compare-against-constant dispatch drift: repeated `cmp imm` chains leading into the same shared tail or case body
  - loop-counter setup drift: `mov cx, imm` / `dec/inc` / `jnz` loops whose bounds change only through relocated literals
  - repeated `movsb`/`movsw` helper setup drift: string/memory copy blocks where the call/setup shape matches but segment/base storage moves
  - far callback install drift: `mov cs:[...], reg` plus `lds/les` setup blocks like `setTimerIrqHanlder`
  - interrupt-vector setup drift: `int 21h`/`int 10h` style call-prep blocks where AH/AL staging remains stable
  - port-I/O setup drift: repeated `mov dx, imm` plus `out`/`in` sequences for hardware init routines
  - multiply-accumulate staging drift: `imul` surrounded by repeated literal/global loads, as seen near `moveStuff`
  - divide/sign-extension staging drift: `cwd`/`idiv` or `xor dx,dx`/`div` setup blocks whose operand sources move
  - shift-mask normalization drift: repeated `and/or/shl/shr/sar` shape around bitfield extraction
  - repeated flag-byte fanout drift: one-byte status values copied into several globals or struct fields
  - repeated segment:offset pair materialization drift: `mov seg`, `mov off`, `les/lds` combinations for far pointers
  - jump-table base setup drift: loading a table base into a register before indexed jumps/calls
  - palette/ramp table walk drift: `si/di/dx` constant setup followed by repeated table iteration
  - local-array base drift: `lea` or `[bp+...]` setup blocks that keep the same local-buffer role while offsets shift
  - repeated two-phase helper call drift: one helper-call setup immediately followed by a second shape-matching helper-call setup
  - boolean materialization drift: same condition role but `sbb/neg/and` vs explicit branch-and-store shape
  - tail-merge drift after error handling: several branches that still reconverge on one cleanup/return tail
  - saved-register pressure drift: extra `push/pop si/di` or saved-register shuffles indicating temp/register allocation changes
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
