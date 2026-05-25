import json
import re

def parse_map_file(map_file_path):
    """Parses a .map file to extract function and data names with correct segment info."""
    symbols = {}
    with open(map_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Handle segment definition lines (e.g., "seg000 CODE 0000")
            seg_match = re.match(r'^(\w+)\s+(CODE|DATA)\s+([0-9a-fA-F]+)$', line)
            if seg_match:
                # Skip segment definitions - we don't need them for symbol parsing
                continue

            # Handle symbol definition lines (must contain colon)
            if ':' not in line:
                continue

            # Split line while preserving quoted sections
            parts = re.split(r'\s+', line)
            if len(parts) < 4:
                continue

            # Extract symbol name (remove trailing colon)
            name = parts[0].rstrip(':')
            
            # Segment is the second token (after symbol name)
            segment = parts[1]
            
            # Address is the fourth token (third token is type like NEAR/FAR)
            addr_str = parts[3]
            
            # Handle address ranges by taking the start address
            if '-' in addr_str:
                addr_str = addr_str.split('-')[0]
                
            # Skip non-hex address parts
            if not re.match(r'^[0-9a-fA-F]+$', addr_str):
                continue
                
            address = int(addr_str, 16)
            symbols[name] = {'segment': segment, 'address': address}
    return symbols

def parse_json_config(json_file_path):
    """Parses the JSON config to get the list of public symbols."""
    with open(json_file_path, 'r') as f:
        config = json.load(f)
    return config.get('publics', [])

def main():
    """Main function to parse files and print symbols."""
    print("Parsing map/egame.map...")
    map_symbols = parse_map_file('map/egame.map')
    print(f"Found {len(map_symbols)} symbols in map file.")

    print("Parsing conf/egame_rc.json...")
    json_publics = parse_json_config('conf/egame_rc.json')
    print(f"Found {len(json_publics)} public symbols in JSON file.")

    print("\n--- Symbols from egame.map ---")
    if map_symbols:
        for name, data in map_symbols.items():
            print(f"  {name}: Segment={data['segment']}, Address=0x{data['address']:04x}")
    else:
        print("  No symbols found.")

    print("\n--- Public symbols from egame_rc.json ---")
    if json_publics:
        for symbol in json_publics:
            print(f"  {symbol}")
    else:
        print("  No public symbols found.")

if __name__ == "__main__":
    main()