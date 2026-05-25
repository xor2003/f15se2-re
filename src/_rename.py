import re
import itertools

# --- The coefficients and constant found by the Z3 solver ---
# This is the "hash function" we are targeting.
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

def generate_suffixes():
    """
    Yields an infinite sequence of alphabetical suffixes:
    _a, _b, ..., _z, _aa, _ab, ...
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    length = 1
    while True:
        for combo in itertools.product(alphabet, repeat=length):
            yield "_" + "".join(combo)
        length += 1

def rename_variables_for_hash_order(data):
    """
    Parses variable data and renames variables by adding suffixes
    to force their hash values into ascending order.
    """
    # --- 1. Parse Input Data ---
    pattern = re.compile(r";?\s*([\w_]+)\s*=\s*(-?\d+)")
    variables = []
    for line in data.strip().split('\n'):
        match = pattern.match(line.strip())
        if match:
            name, offset_str = match.groups()
            variables.append({'name': name, 'offset': int(offset_str)})

    if not variables:
        print("No variables found in the input data.")
        return

    # --- 2. Sort by Stack Offset (Target Order) ---
    variables.sort(key=lambda x: x['offset'], reverse=True)

    # --- 3. Find Suffixes to Enforce Hash Order ---
    renamed_vars = []
    last_hash = -1

    for var in variables:
        original_name = var['name']
        
        # First, check if the original name already works
        original_hash = apply_z3_formula(original_name)
        if original_hash >= last_hash:
            renamed_vars.append({
                'original_name': original_name,
                'new_name': original_name,
                'offset': var['offset'],
                'hash': original_hash
            })
            last_hash = original_hash
            continue

        # If not, find a suffix that works
        suffix_gen = generate_suffixes()
        for suffix in suffix_gen:
            new_name = original_name + suffix
            current_hash = apply_z3_formula(new_name)
            
            if current_hash >= last_hash:
                renamed_vars.append({
                    'original_name': original_name,
                    'new_name': new_name,
                    'offset': var['offset'],
                    'hash': current_hash
                })
                last_hash = current_hash
                break # Found a working suffix, move to the next variable
    
    # --- 4. Print the Report and C Code ---
    max_name_len = max(len(v['new_name']) for v in renamed_vars)
    
    print("--- Variable Renaming Report ---")
    print("The following names have been generated to produce an ascending hash order.\n")
    header = f"{'Offset':<8} | {'Original Name':<18} | {'New Name':<{max_name_len}} | {'Resulting Hash':<17}"
    print(header)
    print("-" * (len(header) + 2))
    
    for var in renamed_vars:
        print(f"{var['offset']:<8} | {var['original_name']:<18} | {var['new_name']:<{max_name_len}} | {var['hash']:<17}")

    print("\n--- Generated C Code ---")
    print("Copy and paste these declarations into your function. The order here now matches the stack layout.")
    print("//----------------------------------------------------------------")
    
    # The list is already sorted by offset, so we just print the new names
    for var in renamed_vars:
        print(f"    int16 {var['new_name']}; // Original offset: {var['offset']}")
    
    print("//----------------------------------------------------------------")

# --- Main Execution ---
if __name__ == "__main__":
    input_data = """
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
    ;	temp_2 = -18
    """
    
    rename_variables_for_hash_order(input_data)