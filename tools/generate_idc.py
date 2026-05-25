import re
import os
import sys
from name_parser import parse_map_file

def parse_segment_starts(map_file_path):
    """Parses the segment start addresses from the .map file with improved regex."""
    segments = {}
    segment_pattern = re.compile(r'^(\w+)\s+(CODE|DATA)\s+([0-9a-fA-F]+)$')
    
    with open(map_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            match = segment_pattern.match(line)
            if match:
                segment_name = match.group(1)
                start_address = int(match.group(3), 16)
                segments[segment_name] = start_address
    return segments

def generate_idc_script(symbols, segments, output_path):
    """Generates an IDA Pro IDC script to rename symbols with error handling."""
    with open(output_path, 'w') as f:
        f.write("#include <idc.idc>\n\n")
        f.write("static main() {\n")
        
        renamed_count = 0
        missing_segments = set()
        
        for name, data in symbols.items():
            segment_name = data['segment']
            if segment_name in segments:
                segment_start = segments[segment_name]
                # Calculate linear address for 16-bit segmented model
                linear_address = (segment_start * 16) + data['address']
                f.write(f"  // Segment: {segment_name}, Offset: 0x{data['address']:04x}\n")
                f.write(f"  MakeName(0x{linear_address:05x}, \"{name}\");\n")
                renamed_count += 1
            else:
                missing_segments.add(segment_name)
        
        f.write("}\n")
        
        return renamed_count, missing_segments

def main():
    """Main function to generate the IDC script with enhanced error reporting."""
    try:
        map_symbols = parse_map_file('map/egame.map')
        segments = parse_segment_starts('map/egame.map')
        
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_idc_path = os.path.join(output_dir, 'rename_symbols.idc')
        renamed_count, missing_segments = generate_idc_script(map_symbols, segments, output_idc_path)
        
        print(f"IDC script generated at: {output_idc_path}")
        print(f"Total symbols processed: {len(map_symbols)}")
        print(f"Symbols successfully renamed: {renamed_count}")
        
        if missing_segments:
            print("\n[!] WARNING: Some segments were not found in the map file:")
            for seg in sorted(missing_segments):
                print(f"  - {seg}")
            print("Symbols in these segments were not included in the IDC script.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()