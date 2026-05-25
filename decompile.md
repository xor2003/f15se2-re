This guide provides a comprehensive, deduplicated set of patterns and heuristics for a reverse engineering agent to reconstruct original C source code from 16-bit DOS x86 assembly. It synthesizes common patterns from early compilers like Microsoft C and Borland C++.

### **Decompilation Guide: Reconstructing 16-bit DOS C Code**

---

#### **1. File & Symbol Analysis (The High-Level View)**

The first step is to understand the file's overall structure from the assembler directives.

*   **Segment Layout:** Identify the standard segments, which map directly to C concepts:
    *   `_TEXT`: Contains all executable code (functions).
    *   `_DATA`: Contains initialized global and static variables.
    *   `_BSS`: Contains uninitialized global and static variables.
    *   `CONST`: Contains constant values.
    *   `DGROUP`: A group that combines `_DATA`, `_BSS`, and `CONST`. The `DS` and `SS` registers are assumed to point here, allowing for direct, near-pointer access to all static and global data.

*   **Symbol Visibility:** Look for symbol declarations to understand the module's dependencies and public interface.
    *   `PUBLIC _symbolName`: A public C function or global variable. The leading underscore is a common convention.
    *   `EXTRN _symbolName:NEAR/WORD`: A call to a function or use of a variable from another object file or library.

*   **Heuristic: Static Variable Aliases (Borland C++):** Borland compilers often leave a crucial hint at the top of the assembly file. This is a direct mapping from the compiler's internal name to the original C name.
    ```assembly
    ; Assembly Clue at top of file
    ;   Static Name Aliases
    ;   $S1024_Dx   EQU Dx
    
    ; Assembly Definition in _DATA segment
    $S1024_Dx   DW  00H
    ```
    When you see `$S1024_Dx` in the code, you can confidently decompile it to the static variable `Dx`.

#### **2. Decompiling Data Structures and Variables**

Reconstructing variables is critical to making the code readable.

*   **Global/Static Variables:** Accessed directly by their symbolic names (e.g., `mov _VX, ax`).

*   **String Literals:** Constant strings are found in the `_DATA` segment with compiler-generated labels.
    ```c
    // C Code
    printf("Unable to open debug stream");
    ```
    ```assembly
    ; In _DATA Segment
    $SG218  DB  'Unable to open debug stream', 00H
    
    ; In _TEXT Segment
    mov     ax, OFFSET DGROUP:$SG218
    push    ax
    call    _printf
    ```

*   **Struct/Union Member Access:** A register (`bx`, `si`, `di`) is loaded with a pointer, and members are accessed via constant offsets from that pointer. By mapping all offsets, you can reconstruct the `struct` layout.
    ```c
    // C Code (Rp is a 'struct RastPort *')
    HCent = (Rp->Width1 + 1) >> 1;
    ```
    ```assembly
    ; Assembly
    mov     bx, WORD PTR [bp+4]     ; Load Rp into bx
    mov     ax, WORD PTR [bx+6]     ; Access member at offset +6 (Width1)
    inc     ax
    sar     ax, 1
    mov     WORD PTR _HCent, ax
    ```

*   **Multi-Dimensional Array Access:** The compiler flattens arrays into a single memory block. Access is calculated by multiplying indices by dimension sizes.
    ```c
    // C Code
    int a[64][64];
    a[x][y] = 123;
    ```
    ```assembly
    ; Assembly
    mov     si, WORD PTR [bp-2]     ; x
    shl     si, 7                   ; si = x * 128 (64 * sizeof(int))
    mov     bx, WORD PTR [bp-4]     ; y
    shl     bx, 1                   ; bx = y * 2 (sizeof(int))
    mov     WORD PTR _a[bx][si], 123 ; Access _a + (x*128) + (y*2)
    ```

#### **3. Reconstructing Functions and Logic**

Functions have a highly predictable structure.

*   **Function Prologue/Epilogue:** Every `near` C function uses a standard entry/exit sequence.
    *   **Prologue:** `push bp`, `mov bp, sp`, `sub sp, <size>`
    *   **Epilogue:** `mov sp, bp` (or `leave`), `pop bp`, `ret`
    The `<size>` in the prologue reveals the total byte size of all local variables.

*   **Parameters and Locals:** Access is relative to the base pointer `bp`.
    *   `[bp+<offset>]`: **Parameter.** `+4` is the first, `+6` the second.
    *   `[bp-<offset>]`: **Local variable.** List all negative offsets to map out the function's local data.

*   **Function Calling Convention (`cdecl`):**
    *   **Argument Passing:** Arguments are `push`ed onto the stack from **right to left**.
    *   **Stack Cleanup:** The **caller** cleans up with `add sp, <size_of_args>`.
    *   **Return Value:** The return value is in `ax` (16-bit) or `dx:ax` (32-bit).

    ```c
    // C Code
    err = intdos(&rin, &rout);
    ```
    ```assembly
    ; Assembly
    mov     ax, OFFSET DGROUP:$S425_rout ; Push &rout (rightmost)
    push    ax
    mov     ax, OFFSET DGROUP:$S424_rin  ; Push &rin (leftmost)
    push    ax
    call    _intdos
    add     sp, 4                        ; Caller cleans up 4 bytes
    mov     WORD PTR [bp-2], ax          ; Store return value in 'err'
    ```

#### **4. Reconstructing Control Flow**

*   **`if` Statements:** A comparison (`cmp` or `test`) followed by a conditional jump that **branches if the condition is false**. The "then" block immediately follows the jump.
    ```c
    // C Code
    if (rout.x.cflag != 0) {
        // True block...
    }
    ```
    ```assembly
    ; Assembly
    cmp     WORD PTR $S425_rout+12, 0
    je      $END_IF         ; Jump if equal (condition is false)
    ; ... true block ...
$END_IF:
    ```

*   **`for` Loops:** Consist of an initializer, a check at the top of the loop, the body, and an increment at the bottom before jumping back to the check.
    ```c
    // C Code
    for (i = 0; i < 63; i++) { /* body */ }
    ```
    ```assembly
    ; i is at [bp-2]
            mov     WORD PTR [bp-2], 0  ; i = 0
            jmp     SHORT $LOOP_CHECK
    $LOOP_BODY:
            ; ... body of loop ...
            inc     WORD PTR [bp-2]     ; i++
    $LOOP_CHECK:
            cmp     WORD PTR [bp-2], 63 ; i < 63
            jl      $LOOP_BODY          ; Jump if less
    ```

*   **`switch` Statements:** For non-sequential cases, the compiler generates a "jump cascade" of comparisons.
    ```c
    // C Code
    switch (TYPE) {
        case 40: SCL = 40; break;
        case 50: SCL = 30; break;
        default: SCL = 4; break;
    }
    ```
    ```assembly
    ; Assembly
    mov     ax, WORD PTR [bp+18]    ; TYPE
    cmp     ax, 50
    je      $CASE_50
    cmp     ax, 40
    jne     $DEFAULT
$CASE_40:
    mov     WORD PTR [bp-2], 40     ; SCL = 40
    jmp     SHORT $END_SWITCH
$CASE_50:
    mov     WORD PTR [bp-2], 30     ; SCL = 30
    jmp     SHORT $END_SWITCH
$DEFAULT:
    mov     WORD PTR [bp-2], 4      ; SCL = 4
$END_SWITCH:
    ```

#### **5. Pointers and Addressing**

*   **Far Pointers (`FAR*`):** Accessing memory in a different segment is a giveaway for `FAR` pointers. The `les` instruction is a definitive sign.
    ```c
    // C Code (mcb is a 'struct MCB FAR *')
    total += mcb->size;
    ```
    ```assembly
    ; Assembly
    les     bx, DWORD PTR [bp-6]    ; Load far pointer mcb into ES:BX
    mov     ax, WORD PTR es:[bx+3]  ; Access member 'size' at offset +3
    add     WORD PTR [bp-10], ax    ; Add to 'total'
    ```

*   **Pointer to Local Variable:** The `lea` (Load Effective Address) instruction gets the address of a local variable, often to pass it as a pointer.
    ```c
    // C Code
    va_list ap;
    va_start(ap, fmt); // ap = (va_list)&fmt + sizeof(fmt);
    ```
    ```assembly
    ; 'ap' is at [bp-2], 'fmt' is parameter at [bp+4]
    lea     ax, WORD PTR [bp+6] ; ax = address of argument after 'fmt'
    mov     WORD PTR [bp-2], ax ; Store address in 'ap'
    ```

*   **Function Pointers:** A `call` that uses a memory operand or register instead of a direct label indicates a function pointer.
    ```c
    // C Code
    gfxInit = overlay_functionAddress(gfxDrvAddress, 0);
    gfxBufAddress = gfxInit(GFX_INIT_ARG);
    ```
    ```assembly
    ; gfxInit is a local far pointer at [bp-14]
    push    WORD PTR _GFX_INIT_ARG
    call    DWORD PTR [bp-14]
    add     sp, 2
    mov     WORD PTR [bp-8], ax ; gfxBufAddress = return value
    ```

#### **6. Recognizing Special Patterns & Idioms**

*   **DOS/BIOS Interaction:**
    *   **DOS Interrupts:** Look for calls to wrappers like `_intdos` and `_intdosx`. The setup involves populating static `union REGS` (`rin`, `rout`) and `struct SREGS` (`sreg`) variables.
    *   **Direct Memory Access:** A hardcoded segment address (especially `0x0000` or `0x0040`) indicates direct hardware or BIOS Data Area access.
    ```c
    // C Code
    uint16 FAR *bios_keyflags = MK_FP(0x0000, 0x0417);
    *bios_keyflags = 0;
    ```
    ```assembly
    ; Assembly
    sub     bx, bx          ; BX = 0
    mov     es, bx          ; ES = 0x0000
    mov     bx, 1047        ; BX = 0x0417
    mov     WORD PTR es:[bx], es ; Write 0 to 0000:0417
    ```

*   **`assert` Macro Expansion:** This is not a function call. It expands into an inline `if` statement that, if the condition fails, pushes arguments and calls `_fprintf` and `_abort`.

*   **32-bit Math on 16-bit Hardware:** Long integer operations use the `dx:ax` register pair. A 32-bit left shift (multiplication) is implemented as a loop that shifts `ax` and rotates the carry bit into `dx`.

*   **"Magic Number" Signatures:** Hardcoded, unusual numbers written to memory are often signatures used by another part of the program to verify that a data structure is valid and has been initialized correctly.

*   **Empty Function Stubs:** An exported (`PUBLIC`) function that contains only a `ret` is likely an intentional stub. This was a common memory-saving trick to prevent the linker from including a large library module when it was not needed.
