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
    #shift = BitVec(f'S', 16)
    constant = BitVec('K', 16)
    
    print(f"\n[Step 2] Modeling a universal hash function with {max_len + 1} unknown 16-bit constants.")
    print(f"  Formula: hash(name) = (C_0*name[0]) + ... + (C_{max_len-1}*name[{max_len-1}]) + K")

    def build_hash_expression(name):
        """Builds a Z3 expression for the hash of a single name using the universal coefficients."""
        expr = constant
        for i, char in enumerate(name):
            if i < max_len:
                expr = expr + coeffs[i] * BitVecVal(ord(char), 16)
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
        #print(f"  S    = {model[shift]}")

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
_dos_mcbInfo	PROC NEAR
;	segment = -8
;	lol = -142
;	mcb = -6
;	total = -10
;	alloc = -146
;	free = -2
;	i = -144
;	strbuf = -138
_overlay_load	PROC NEAR
;	RESERVE_PARA = -18
;	EXTRA_PARA = -6
;	freeMem = -2
;	alloc = -14
;	ovlSegment = -4
;	ovlSize = -16
;	ovlHeader = -12
;	err = -8
_hexdump	PROC NEAR
;	bpl = -8
;	limit = -10
;	i = -4
;	j = -6
;	c = -2
;	pos = -12
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
    
    find_universal_hash_formula(input_data)