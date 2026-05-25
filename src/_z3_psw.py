import re
from z3 import *

def find_universal_reversed_pjw_constants(data):
    """
    Uses the Z3 SMT solver to find parameters for a reversed PJW-like hash
    that explains the stack variable ordering across ALL provided functions.
    """
    print("="*70)
    print("--- Z3 Search for Reversed PJW Constants ---")
    print("="*70)

    # --- Step 1: Parse All Functions and their Variables ---
    functions = {}
    current_function = None
    func_pattern = re.compile(r'^(\w+)\s+PROC NEAR')
    var_pattern = re.compile(r";?\s*([\w_]+)\s*=\s*(-?\d+)")

    for line in data.strip().split('\n'):
        line = line.strip()
        func_match = func_pattern.match(line)
        var_match = var_pattern.match(line)
        
        if func_match:
            current_function = func_match.group(1)
            if current_function not in functions:
                functions[current_function] = []
        elif var_match and current_function:
            name, offset_str = var_match.groups()
            functions[current_function].append({
                'name': name,
                'offset': int(offset_str)
            })
            
    # Filter out functions with fewer than 2 variables
    constrained_functions = {k: v for k, v in functions.items() if len(v) >= 2}
    
    print(f"\n[Step 1] Parsed {len(constrained_functions)} functions with enough variables to create constraints.")

    # --- Step 2: Define the Parametric Reversed PJW Model ---
    all_names = [var['name'] for func_vars in constrained_functions.values() for var in func_vars]
    max_len = max(len(name) for name in all_names) if all_names else 0

    # Z3 variables for PJW parameters (16-bit unsigned)
    left_shift = BitVec('LS', 16)
    high_bits = BitVec('HB', 16)
    right_shift = BitVec('RS', 16)
    initial_hash = BitVec('IH', 16)
    
    print(f"\n[Step 2] Modeling reversed PJW hash with 4 unknown 16-bit parameters.")
    print(f"  Structure: h = IH; for char in reversed(name): h = (h << LS) + char; g = h & mask(HB); if g != 0: h ^= (g >> RS); h &= ~g")

    def build_hash_expression(name):
        """Builds a Z3 expression for the reversed PJW hash of a name."""
        # Reverse the name as per "reversed PJW"
        rev_name = name[::-1]
        
        # Compute symbolic mask: ((1 << HB) - 1) << (16 - HB)
        one = BitVecVal(1, 16)
        sixteen = BitVecVal(16, 16)
        mask = ((one << high_bits) - one) << (sixteen - high_bits)
        
        expr = initial_hash
        for char in rev_name:
            char_val = BitVecVal(ord(char), 16)
            expr = (expr << left_shift) + char_val
            g = expr & mask
            expr = If(g != 0, expr ^ (g >> right_shift), expr)
            expr = expr & ~g
        return expr

    # --- Step 3: Create Solver and Add All Constraints ---
    solver = Solver()
    total_constraints = 0
    
    # Add reasonable bounds to help solver (based on standard PJW)
    solver.add(left_shift >= 1, left_shift <= 8)
    solver.add(high_bits >= 1, high_bits <= 8)
    solver.add(right_shift >= 1, right_shift <= 15)
    # initial_hash can be 0-65535, no bound needed
    
    print("\n[Step 3] Adding all ordering constraints from all functions to a single solver...")
    
    for func_name, variables in sorted(constrained_functions.items()):
        # Sort by offset descending (top of stack first, assumed lower hash)
        variables.sort(key=lambda x: x['offset'], reverse=True)
        
        # Build hash expressions
        hash_expressions = {v['name']: build_hash_expression(v['name']) for v in variables}
        
        # Add constraints: hash_current <= hash_next (ascending hash in sorted list)
        for i in range(len(variables) - 1):
            var_current = variables[i]
            var_next = variables[i+1]
            constraint = ULE(hash_expressions[var_current['name']], hash_expressions[var_next['name']])
            solver.add(constraint)
            total_constraints += 1

    print(f"  - Successfully added {total_constraints} constraints from {len(constrained_functions)} functions.")

    # --- Step 4: Run the Solver and Report Final Results ---
    print("\n[Step 4] Asking Z3 to find parameters satisfying all constraints...")
    result = solver.check()
    
    print("\n" + "="*70)
    print("--- Final Z3 Solver Results ---")
    print("="*70)

    if result == sat:
        print("Status: SATISFIABLE ('sat')")
        model = solver.model()
        print("\nFound reversed PJW parameters:")
        print(f"  Left Shift (LS): {model[left_shift]}")
        print(f"  High Bits (HB): {model[high_bits]}")
        print(f"  Right Shift (RS): {model[right_shift]}")
        print(f"  Initial Hash (IH): {model[initial_hash]}")
        print("These values satisfy the ordering for ALL functions when applied to reversed names.")

    elif result == unsat:
        print("Status: UNSATISFIABLE ('unsat')")
        print("\nNo single set of reversed PJW parameters exists that satisfies the variable stack ordering across all functions.")

    else:
        print(f"Status: UNKNOWN ('{result}')")
        print("The solver could not determine a solution; try simplifying bounds or fixing some parameters.")

# --- Main Execution ---
if __name__ == "__main__":
    # The complete multi-function data provided by the user
    # Note: Manually renamed duplicate function names if needed
    input_data = """
_bios_clearkeyflags	PROC NEAR
;	bios_keyflags = -4
_dos_alloc	PROC NEAR
;	err = -2
_dos_free	PROC NEAR
;	err = -2
_dos_resize	PROC NEAR
;	err = -2
_dos_getfree	PROC NEAR
;	err = -2
loadprog	PROC NEAR
;	err = -2
_dos_loadOverlay	PROC NEAR
_dos_runProgram	PROC NEAR
_dos_loadProgram	PROC NEAR
;	err = -2
_dos_getReturnCode	PROC NEAR
;	err = -2
_dos_getProcessId	PROC NEAR
_dos_setProcessId	PROC NEAR
dos_sysvars	PROC NEAR
_dos_mcbInfo	PROC NEAR
;	segment = -8
;	lol = -142
;	mcb = -6
;	total = -10
;	alloc = -146
;	free = -2
;	i = -144
;	strbuf = -138
_dos_lastFreeBlock	PROC NEAR
;	segment = -6
;	lol = -10
;	mcb = -4
_dos_envSize	PROC NEAR
;	envSegment = -6
;	envMcb = -4
_load_driver	PROC NEAR
;	drvAddress = -6
;	commPtr = -4
_game_init	PROC NEAR
;	gfxDrvAddress = -6
;	gfxBufAddress = -8
;	err = -10
;	freeMemory = -16
;	charPtr = -4
;	gfxInit = -14
_game_run	PROC NEAR
;	err = -2
_load_segment	PROC NEAR
_main	PROC NEAR
;	i = -6
;	j = -8
;	debugMenu = -10
;	debugFlight = -2
;	debugDebrief = -4
;	arg = -12
;	len = -14
_output_stdout	PROC NEAR
_log_open	PROC NEAR
_log_close	PROC NEAR
_output_log	PROC NEAR
_output_tee	PROC NEAR
_output	PROC NEAR
;	ap = -2
_INFO	PROC NEAR
;	ap = -2
_ERROR	PROC NEAR
;	ap = -2
_FATAL	PROC NEAR
;	ap = -2
_DEBUG	PROC NEAR
;	ap = -2
_dumpregs	PROC NEAR
_hexdump	PROC NEAR
;	bpl = -8
;	limit = -10
;	i = -4
;	j = -6
;	c = -2
;	pos = -12
_overlay_load	PROC NEAR
;	RESERVE_PARA = -18
;	EXTRA_PARA = -6
;	freeMem = -2
;	alloc = -14
;	ovlSegment = -4
;	ovlSize = -16
;	ovlHeader = -12
;	err = -8
_overlay_functionAddress	PROC NEAR
;	ovlHeader = -8
;	slotArray = -4
_strcpyFar	PROC NEAR
;	dest = -4
_memcpyFar	PROC NEAR
;	dest = -4
_writeWordFar	PROC NEAR
;	wordPtr = -4
_blitFileFar	PROC NEAR
;	dest = -4
;	buffer = -268
;	infile = -8
;	readsize = -6
;	i = -12
;	err = -10
_sizeString	PROC NEAR
;	bytes = -4
_otherKeyDispatch	PROC NEAR
;	temp_2 = -18
;	var_3E = -4
;	var_3C = -48
;	var_38 = -14
;	var_34 = -54
;	var_32 = -42
;	var_2C = -40
;	var_2A = -32
;	var_28 = -12
;	var_24 = -46
;	var_22 = -34
;	var_20 = -28
;	var_1A = -26
;	var_18 = -8
;	var_16 = -52
;	var_14 = -38
;	var_10 = -24
;	var_E = -36
;	var_C = -30
;	temp_ax = -44
;	temp_bx = -50
;	temp_cx = -2
;	temp_long_dx_ax = -22
;	temp_1 = -16
    """
    
    find_universal_reversed_pjw_constants(input_data)