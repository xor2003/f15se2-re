#!/usr/bin/env python3
import re
import sys

def parse_pat_line(line):
    """Parse a line from a PAT file using named regex groups."""
    print(line)
    pattern = re.compile(
        r"^(?P<pattern_bytes>[0-9A-F\.]+)\s"                 # Pattern bytes (first 64 characters)
        r"(?P<alen>[0-9A-F]{2})\s"                           # ALEN (2 characters)
        r"(?P<asum>[0-9A-F]{4})\s"                           # ASUM (4 characters)
        r"(?P<total_length>[0-9A-F]{4})"                   # Total length of the module (4 characters)
        r"(?:\s([:^][0-9A-F]{4} [0-9A-Za-z_]+))*"           # List of referenced names (can be empty)
        r"(?:\s(?P<tail_bytes>[0-9A-F\.]*))$"                        # Tail bytes (variable-length)
    )
    
    match = pattern.match(line)
    if match:
        result = {
            "pattern_bytes": match.group("pattern_bytes"),
            "total_length": match.group("total_length"),
            "tail_bytes": match.group("tail_bytes") or ''
        }
        print(result)
        return result
    else:
        print(line)
        return None

def compare_bytes_with_dots(byte_seq1, byte_seq2):
    """Compare two byte sequences with support for dots as variable bytes."""
    if len(byte_seq1) != len(byte_seq2):
        return False

    for b1, b2 in zip(byte_seq1, byte_seq2):
        if b1 != '.' and b2 != '.' and b1 != b2:
            return False
    return True

def compare_patterns(file1, file2):
    """Compare two PAT files line by line based on the provided rules."""
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    # Ensure both files have the same number of lines
    if len(lines1) != len(lines2):
        print("Files have different numbers of lines.")
        sys.exit(2)

    for i, (line1, line2) in enumerate(zip(lines1, lines2)):
        if line1 == '---\n':
           continue
        data1 = parse_pat_line(line1)
        data2 = parse_pat_line(line2)

        if not data1 or not data2:
            print(f"Line {i + 1}: Failed to parse one or both lines.")
            sys.exit(3)

        # Compare the total length of the module
        if data1["total_length"] != data2["total_length"]:
            print(f"Line {i + 1}: Total lengths differ - File1: {data1['total_length']} File2: {data2['total_length']}")
            sys.exit(4)

        # Compare pattern bytes (first 64 characters), allowing dots as variable bytes
        if not compare_bytes_with_dots(data1["pattern_bytes"], data2["pattern_bytes"]):
            print(f"Line {i + 1}: Pattern bytes differ.\n{data1["pattern_bytes"]}\n{data2["pattern_bytes"]}")
            sys.exit(5)

        # Compare tail bytes based on the minimal length of both
        min_tail_length = min(len(data1["tail_bytes"]), len(data2["tail_bytes"]))
        tail1 = data1["tail_bytes"][-min_tail_length:]
        tail2 = data2["tail_bytes"][-min_tail_length:]
        if not compare_bytes_with_dots(tail1, tail2):
            print(f"Line {i + 1}: Tail bytes differ.\n{tail1}\n{tail2}")
            sys.exit(6)
    print("Equal.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_pat.py <file1.pat> <file2.pat>")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    compare_patterns(file1, file2)
