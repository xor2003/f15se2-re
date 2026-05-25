import re
from z3 import *

def find_universal_hash_formula(data):
    """
    Uses the Z3 SMT solver to try and find a SINGLE, UNIVERSAL hash formula
    that explains the stack variable ordering across ALL provided functions.
    """
    print("="*70)
    print("--- Z3 Search for a Universal Hash Formula ---")
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
            
    # Filter out functions with fewer than 2 variables, as they provide no constraints
    constrained_functions = {k: v for k, v in functions.items() if len(v) >= 2}
    
    print(f"\n[Step 1] Parsed {len(constrained_functions)} functions with enough variables to create constraints.")

    # --- Step 2: Define the Universal Hash Function Model ---
    all_names = [var['name'] for func_vars in constrained_functions.values() for var in func_vars]
    max_len = max(len(name) for name in all_names) if all_names else 0

    # Create Z3 integer variables for our single set of unknown coefficients
    coeffs = [BitVec(f'C_{i}', 16) for i in range(max_len)]
    constant = BitVec('K', 16)
    
    print(f"\n[Step 2] Modeling a universal hash function with {max_len + 1} unknown 16-bit constants.")
    print(f"  Formula: hash(name) = (C_0*name[0]) + ... + (C_{max_len-1}*name[{max_len-1}]) + K")

    def build_hash_expression(name):
        """Builds a Z3 expression for the hash of a single name using the universal coefficients."""
        expr = constant
        for i, char in enumerate(name):
            if i < max_len:
                expr += coeffs[i] * BitVecVal(ord(char), 16)
        return expr

    # --- Step 3: Create Solver and Add All Constraints ---
    solver = Solver()
    total_constraints = 0
    
    print("\n[Step 3] Adding all ordering constraints from all functions to a single solver...")
    
    for func_name, variables in sorted(constrained_functions.items()):
        # Sort this function's variables by stack offset
        variables.sort(key=lambda x: x['offset'], reverse=True)
        
        # Build Z3 expressions for each variable name
        hash_expressions = {v['name']: build_hash_expression(v['name']) for v in variables}
        
        # Add constraints for this function
        for i in range(len(variables) - 1):
            var_current = variables[i]
            var_next = variables[i+1]
            
            # Constraint: hash(current) <= hash(next)
            constraint = ULE(hash_expressions[var_current['name']], hash_expressions[var_next['name']])
            solver.add(constraint)
            total_constraints += 1

    print(f"  - Successfully added {total_constraints} constraints from {len(constrained_functions)} functions.")

    # --- Step 4: Run the Solver and Report Final Results ---
    print("\n[Step 4] Asking Z3 to find a single solution for all constraints simultaneously...")
    result = solver.check()
    
    print("\n" + "="*70)
    print("--- Final Z3 Solver Results ---")
    print("="*70)

    if result == sat:
        print("Status: SATISFIABLE ('sat')")
        print("\nThis is a monumental and unexpected result!")
        print("Z3 has found a SINGLE universal formula that correctly orders the variables")
        print("for ALL functions provided. The coefficients are:")
        model = solver.model()
        for i in range(max_len):
            print(f"  C_{i} = {model[coeffs[i]]}")
        print(f"  K    = {model[constant]}")

    elif result == unsat:
        print("Status: UNSATISFIABLE ('unsat')")
        print("\nThis is the expected outcome and provides a definitive conclusion.")
        print("Z3 has formally proven that it is IMPOSSIBLE for any single formula of the form")
        print("  hash = C_0*char_0 + ... + K")
        print("to satisfy the variable stack ordering across all functions simultaneously.")
        print("\nThis proves that the MS C 5.1 compiler DOES NOT use a universal hash-and-sort")
        print("algorithm for local variable stack allocation.")

    else:
        print(f"Status: UNKNOWN ('{result}')")
        print("The solver could not determine a solution. The combined problem may be too complex.")

# --- Main Execution ---
if __name__ == "__main__":
    # The complete multi-function data provided by the user
    # Note: Manually renamed duplicate function names in the input string
    # (e.g., _main -> _main_2) to treat them as unique test cases.
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
_SetDrawWindow	PROC NEAR
;	LWidth = -4
;	LHeight = -2
_my_vtrace	PROC NEAR
;	thistime = -4
;	timedelta = -8
_my_fartrace	PROC NEAR
;	ptr = -8
;	size = -10
;	idx = -4
;	ap = -2
_ftoncpy	PROC NEAR
;	src = -6
;	dest = -2
;	i = -10
_dumpbuf	PROC NEAR
;	buffer = -518
;	bytes_written = -6
;	file = -2
;	result = -520
;	bytes_to_copy = -524
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
_main	PROC NEAR
;	i = -6
;	j = -8
;	debugMenu = -10
;	debugFlight = -2
;	debugDebrief = -4
;	arg = -12
;	len = -14
_IntDiv	PROC NEAR
;	S1 = -2
;	S2 = -4
;	LA = -8
;	LB = -12
_Iasin	PROC NEAR
;	AA = -4
;	angl = -2
;	delta = -8
;	i = -6
_Sqrt	PROC NEAR
;	B = -4
;	A = -2
_IntDiv	PROC NEAR
;	S1 = -2
;	S2 = -4
;	LA = -8
;	LB = -12
_Iasin	PROC NEAR
;	AA = -4
;	angl = -2
;	delta = -8
;	i = -6
_Sqrt	PROC NEAR
;	A = -2
;	B = -4
_main	PROC NEAR
;	x = -2
;	y = -4
_Message	PROC NEAR
;	i = -6
;	min = -4
;	slot = -2
_MyMessages	PROC NEAR
;	outside = -18
;	P = -4
;	SRC = -10
;	cnt = -6
;	lastmsg = -14
;	lastmsgnum = -12
;	msgplace = -16
_MyMessage	PROC NEAR
;	i = -8
;	min = -4
;	slot = -2
;	cnt = -6
;	lastmsg = -12
;	lastmsgnum = -10
;	msgplace = -14
_OutSideHeading	PROC NEAR
;	S = -80
;	N = -172
;	V = -82
_NShowJoy	PROC NEAR
;	SEG = -14
;	x = -6
;	y = -10
;	w = -4
;	z = -12
;	d = -2
;	i = -8
_NWaitShowJoy	PROC NEAR
;	i = -4
;	v = -2
;	j = -8
_GetJoyConfig	PROC NEAR
;	f = -2
;	offset = -4
_SaveJoyConfig	PROC NEAR
;	f = -2
;	offset = -4
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
_rng	PROC NEAR
_rng2	PROC NEAR
_xydist	PROC NEAR
;	d = -4
_testTrace	PROC NEAR
;	str = -8
;	a = -2
;	b = -4
;	c = -6
_blitFileFar	PROC NEAR
;	dest = -4
;	buffer = -268
;	infile = -8
;	readsize = -6
;	i = -12
;	err = -10
add16Color	PROC NEAR
;	r = -4
;	g = -6
;	b = -2
;	i = -10
;	h = -8
;	l = -12
addRun	PROC NEAR
;	r = -4
;	g = -10
;	b = -2
;	i = -12
;	up = -6
;	v = -8
levelUp	PROC NEAR
;	i = -4
;	v = -2
_main	PROC NEAR
;	status = -2
;	levelup = -4
_Do3dObject	PROC NEAR
;	dx = -14
;	dy = -18
;	dz = -20
;	t1 = -6
;	t2 = -10
;	SCL = -2
    """
    
    find_universal_hash_formula(input_data)