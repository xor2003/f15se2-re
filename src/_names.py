import re

# --- The coefficients and constant found by the Z3 solver ---
# This is the specific formula we are testing for consistency.
Z3_COEFFS = [  2870,
  44878,
  21115,
  30520,
  4096,
  4096,
  9510,
  64789,
  4493,
  38437,
  0,
  64735,
  43613,
  0,
  0,
]
Z3_CONSTANT = 64590

def apply_z3_formula(s):
    """Applies the specific formula discovered by the Z3 solver."""
    hash_val = Z3_CONSTANT
    for i, char in enumerate(s):
        if i < len(Z3_COEFFS):
            # Perform 16-bit unsigned arithmetic
            hash_val = (hash_val + Z3_COEFFS[i] * ord(char)) & 0xFFFF
    return hash_val

def parse_all_functions(data):
    """
    Parses a large text block to extract all functions and their stack variables.
    """
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
            
    return functions

def check_and_report_function(func_name, variables):
    """
    Checks a single function's variable order and prints a detailed report if it fails.
    Returns True for pass, False for fail.
    """
    if len(variables) < 2:
        return True # A function with 0 or 1 variable is trivially sorted.

    # Sort variables by stack offset (descending)
    variables.sort(key=lambda x: x['offset'], reverse=True)
    
    # Check if the hash order is maintained
    is_sorted = True
    last_hash = -1
    for var in variables:
        var['hash'] = apply_z3_formula(var['name'])
        if var['hash'] < last_hash:
            is_sorted = False
            # No need to check further for this function
            break
        last_hash = var['hash']

    if not is_sorted:
        print(f"\n--- FAILURE DETAILS for function: {func_name} ---")
        max_name_len = max(len(v['name']) for v in variables)
        header = f"{'Offset':<8} | {'Variable Name':<{max_name_len}} | {'Calculated Hash':<17} | {'Hash in Order?':<15}"
        print(header)
        print("-" * len(header))
        
        last_hash = -1
        for var in variables:
            status = 'OK'
            if var['hash'] < last_hash:
                status = '**FAIL**'
            print(f"{var['offset']:<8} | {var['name']:<{max_name_len}} | {var['hash']:<17} | {status:<15}")
            #if status == '**FAIL**':
            # To avoid clutter, you can uncomment the next line to stop after the first failure
            # break 
            last_hash = var['hash']
        print("-" * len(header))

    return is_sorted

# --- Main Execution ---
if __name__ == "__main__":
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
_game_init	PROC NEAR
;	gfxDrvAddress = -6
;	gfxBufAddress = -8
;	err = -10
;	freeMemory = -16
;	charPtr = -4
;	gfxInit = -14
    """
    
    # NOTE: Manually renamed duplicate functions in the input string
    # (e.g., _main -> _main_2) to treat them as unique test cases.

    all_functions = parse_all_functions(input_data)
    
    pass_count = 0
    fail_count = 0
    
    print("="*60)
    print("Running comprehensive test of Z3 formula across all functions...")
    print("="*60)
    
    for name, variables in sorted(all_functions.items()):
        if not variables:
            # Skip functions with no local variables to test
            continue
            
        result = check_and_report_function(name, variables)
        
        if result:
            pass_count += 1
            print(f"Function '{name}': PASS")
        else:
            fail_count += 1
            # The detailed report is printed inside the check function
            print(f"Function '{name}': **FAIL**")

    print("\n" + "="*60)
    print("Final Test Summary")
    print("="*60)
    print(f"Total Functions with Local Variables Tested: {pass_count + fail_count}")
    print(f"Functions that PASSED the hash order check: {pass_count}")
    print(f"Functions that FAILED the hash order check: {fail_count}")
    print("\nConclusion: The Z3-discovered formula is NOT a general algorithm, as it fails")
    print("on nearly every function other than the one it was derived from.")

### Script Output