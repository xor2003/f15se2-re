import re
import sys
from name_parser import parse_map_file, parse_json_config

def parse_lst_file(lst_file_path):
    """Parses a .lst file to extract symbols, handling both hex and decimal addresses."""
    symbols = {}
    with open(lst_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Match both hex (0xFFFF) and decimal (65535) addresses
            match = re.match(r'([0-9a-fA-F]{4}):([0-9a-fA-F]{1,4}|[0-9]{1,5})\s+([a-zA-Z0-9_]+)', line)
            if match:
                segment = match.group(1)
                address_str = match.group(2)
                name = match.group(3)
                
                # Determine if address is hex (has letters) or decimal
                if any(c in 'abcdefABCDEF' for c in address_str):
                    address = int(address_str, 16)
                else:
                    address = int(address_str)
                    
                symbols[name] = {'segment': segment, 'address': address}
    return symbols

def main():
    """Main function to check for name discrepancies with improved validation."""
    try:
        map_symbols = parse_map_file('map/egame.map')
        json_publics = parse_json_config('conf/egame_rc.json')
        lst_symbols = parse_lst_file('lst/egame.lst')
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- Symbol Validation Report ---")
    
    # 1. Check for address mismatches between map and lst
    mismatched_addresses = []
    for name, map_data in map_symbols.items():
        if name in lst_symbols:
            if lst_symbols[name]['address'] != map_data['address']:
                mismatched_addresses.append((
                    name,
                    f"0x{map_data['address']:04x}",
                    f"0x{lst_symbols[name]['address']:04x}"
                ))
    
    # 2. Check for symbols missing in LST
    missing_in_lst = [
        name for name in map_symbols
        if name not in lst_symbols and name in json_publics
    ]
    
    # 3. Check for JSON public symbols missing in LST
    missing_json_in_lst = [
        name for name in json_publics
        if name not in lst_symbols
    ]
    
    # 4. Check for symbols in LST but missing from authoritative sources
    extra_in_lst = [
        name for name in lst_symbols
        if name not in map_symbols and name not in json_publics
    ]

    # Print report
    if mismatched_addresses:
        print("\n[!] ADDRESS MISMATCHES (Map vs LST):")
        for name, map_addr, lst_addr in mismatched_addresses:
            print(f"  {name}: Map={map_addr}, LST={lst_addr}")
    else:
        print("\n[✓] All addresses match between map and lst files")
    
    if missing_in_lst:
        print("\n[!] SYMBOLS MISSING IN LST (from map):")
        for name in missing_in_lst:
            print(f"  {name}")
    else:
        print("\n[✓] All map symbols present in lst file")
    
    if missing_json_in_lst:
        print("\n[!] PUBLIC SYMBOLS MISSING IN LST (from JSON):")
        for name in missing_json_in_lst:
            print(f"  {name}")
    else:
        print("\n[✓] All JSON public symbols present in lst file")
    
    if extra_in_lst:
        print("\n[!] EXTRA SYMBOLS IN LST (not in map or JSON):")
        for name in extra_in_lst:
            print(f"  {name}")
    else:
        print("\n[✓] No unexpected symbols found in lst file")

    print("\nValidation complete.")

if __name__ == "__main__":
    main()