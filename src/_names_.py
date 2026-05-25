#!/usr/bin/env python3
import re

def djb2_16bit(s):
    """
    Calculates a 16-bit DJB2 hash for a given string.
    
    The algorithm is: hash = ((hash << 5) + hash) + char
    All operations are performed on 16-bit unsigned integers.
    """
    hash_val = 5381
    for char in s:
        # Perform the DJB2 operation and ensure it wraps around at 16 bits (65536)
        hash_val = (((hash_val << 5) + hash_val) + ord(char)) & 0xFFFF
    return hash_val

def check_variable_hash_order(data):
    """
    Parses variable data, calculates hashes, and checks if the stack
    order matches the hash order.
    """
    # Regex to capture variable name and its decimal offset
    # Handles optional leading semicolon and whitespace
    pattern = re.compile(r";?\s*([\w_]+)\s*=\s*(-?\d+)")
    
    variables = []
    
    # --- 1. Parse Input and Calculate Hashes ---
    for line in data.strip().split('\n'):
        match = pattern.match(line.strip())
        if match:
            name, offset_str = match.groups()
            offset = int(offset_str)
            hash_val = djb2_16bit(name)
            variables.append({
                'name': name,
                'offset': offset,
                'hash': hash_val,
                'status': '' # Will be filled in later
            })

    if not variables:
        print("No variables found in the input data.")
        return

    # --- 2. Sort by Stack Offset ---
    # The stack grows downwards from the base pointer (bp), so [bp-2] is at a
    # higher memory address than [bp-4]. We sort in descending order of the
    # offset value to get the correct memory layout from high to low.
    variables.sort(key=lambda x: x['offset'], reverse=True)

    # --- 3. Verify Hash Order ---
    is_sorted_by_hash = True
    last_hash = -1 # Start with a value lower than any possible hash

    for var in variables:
        if var['hash'] < last_hash:
            is_sorted_by_hash = False
            var['status'] = '**FAIL**'
        else:
            var['status'] = 'OK'
        last_hash = var['hash']
        
    # --- 4. Print the Report ---
    # Find the longest variable name for clean formatting
    max_name_len = max(len(var['name']) for var in variables) if variables else 10
    
    print("--- Verifying Stack Variable Order vs. 16-bit DJB2 Hash ---\n")
    header = f"{'Offset':<8} | {'Variable Name':<{max_name_len}} | {'16-bit DJB2 Hash':<17} | {'Hash in Order?':<15}"
    print(header)
    print("-" * len(header))
    
    for var in variables:
        print(f"{var['offset']:<8} | {var['name']:<{max_name_len}} | {var['hash']:<17} | {var['status']:<15}")
        
    print("\n" + "-" * len(header))
    print("\n--- Conclusion ---")
    if is_sorted_by_hash:
        print("The variables APPEAR to be sorted by the 16-bit DJB2 hash.")
    else:
        print("The variables ARE NOT sorted by the 16-bit DJB2 hash.")
        print("The first failure in the sequence is marked with **FAIL**.")

# --- Main Execution ---
if __name__ == "__main__":
    # Paste the multi-line data here
    input_data = """
;	r = -4
;	g = -10
;	b = -2
;	i = -12
;	up = -6
;	v = -8
    """
    
    check_variable_hash_order(input_data)