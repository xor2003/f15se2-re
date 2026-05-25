import re

def get_alpha_suffix(index):
    """
    Generates an alphabetical suffix based on an index.
    0 -> '_a', 1 -> '_b', ..., 25 -> '_z', 26 -> '_aa', 27 -> '_ab', etc.
    """
    if index < 0:
        return ""
    
    result = ""
    while True:
        remainder = index % 26
        result = chr(ord('a') + remainder) + result
        index = (index // 26) - 1
        if index < 0:
            break
            
    return "_" + result

def generate_sorted_declarations(data):
    """
    Parses a list of variables and their stack offsets, then renames them
    with an alphabetical suffix to enforce stack order when sorted by name.

    Args:
        data (str): A multi-line string containing the variable assignments.

    Returns:
        str: A formatted string of C-style variable declarations.
    """
    # Regex to capture variable name and its decimal offset
    pattern = re.compile(r";?\s*([\w_]+)\s*=\s*(-?\d+)")
    
    variables = []
    
    # 1. Parse the input data to extract names and offsets
    for line in data.strip().split('\n'):
        match = pattern.match(line.strip())
        if match:
            name, offset_str = match.groups()
            variables.append({'name': name, 'offset': int(offset_str)})

    if not variables:
        return "No variables found in the input data."

    # 2. Sort variables by stack offset in descending order.
    # This places [bp-2] before [bp-4], matching the memory layout.
    variables.sort(key=lambda x: x['offset'], reverse=True)

    output_lines = ["// Automatically renamed variables to enforce stack order:", ""]
    
    # 3. Generate new names with suffixes and create declaration strings
    for i, var in enumerate(variables):
        original_name = var['name']
        original_offset = var['offset']
        
        # Generate the suffix (e.g., _a, _b, ...) based on the sorted order
        suffix = get_alpha_suffix(i)
        
        new_name = f"{original_name}{suffix}"
        
        # Assume 'int16' as the type. You may need to adjust this.
        # Note: The 'register' keyword should be added manually where needed.
        declaration = f"int16 {new_name};".ljust(40) + f"// Original: {original_name}, Offset: {original_offset}"
        output_lines.append(declaration)
        
    return "\n".join(output_lines)

# --- Main Execution ---
if __name__ == "__main__":
    # Paste your list of variables for a specific function here
    input_data = """
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
    
    new_declarations = generate_sorted_declarations(input_data)
    print(new_declarations)