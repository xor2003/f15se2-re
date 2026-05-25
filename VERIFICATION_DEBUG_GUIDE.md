# DOS Executable Verification Debug Guide

## Understanding "Mismatch" Messages

### What "Mismatch" Actually Means
The "Comparison result: mismatch" message indicates **byte-level data differences** between your reference executable and target executable. This is **not** a code comparison issue - it's specifically detecting that at least one byte in the data segments differs between the two files.

### Enhanced Error Messages (After Improvements)
The verification tool now provides detailed mismatch information:

```
DATA MISMATCH DETECTED:
  Location: 1234:5678 (ref) vs 1234:5678 (tgt)
  Byte position: 42 of 1024 (4.1%)
  Expected: 0x41, Found: 0x42
  Variable: myVariable (exact match)
```

### Common Causes of Mismatches

1. **Different Build Timestamps**: DOS executables often embed build dates/times
2. **Padded Data**: Different compilers may pad data segments differently
3. **String Literals**: Version strings or path differences
4. **Checksum Data**: Embedded checksums that change with each build
5. **Resource Data**: Icons, bitmaps, or other resources that differ

## Debug Message Reference

### Progress Messages
- `DEBUG: Dumping visited map...` - Code exploration phase complete, saving discovered routines
- `Building code map from search queue contents: X routines over Y segments` - Summary of discovered code
- `WARNING: Unable to find segment for offset...` - Memory layout issue (usually harmless)
- `Saving target map to...` - Intermediate analysis files being written

### Comparison Messages
- `VERIFICATION SUCCESS: All data segments match` - No differences found
- `VERIFICATION FAILED: Executable data verification failed` - Differences detected (see detailed output above)

### Detailed Mismatch Information
When a mismatch occurs, you'll see:
- **Exact memory address** where the difference occurs
- **Byte position** within the segment (helps locate the issue)
- **Expected vs actual values** in hexadecimal
- **Variable context** if the mismatch is near known variables

## Troubleshooting Steps

### 1. Identify the Mismatch Location
Look for the detailed mismatch output:
```
Location: 1234:5678
Byte position: 42 of 1024
```

### 2. Examine the Hex Dump
The tool provides a hex dump around the mismatch location:
```
Address    Reference    Target
1234:5670  41 42 43 44  41 42 43 45
                 ^ mismatch here
```

### 3. Check Variable Context
If the mismatch is near a known variable, the tool will identify it:
```
Variable: gameVersionString
```

### 4. Common Fixes
- **Timestamp differences**: Use a tool to normalize timestamps before comparison
- **Padding differences**: Focus on actual data content, ignore padding
- **Version strings**: Update reference to match expected version
- **Checksum data**: Exclude checksum areas from comparison if appropriate

## Advanced Debugging

### Using the Generated Files
- `map/egame.tgt` - Contains the analyzed target executable map
- `map/egame.ref` - Contains the analyzed reference executable map
- These can be examined to understand the structure and locate specific variables

### Variable Analysis
The tool tracks variables and their locations, which helps identify:
- Global variables that might differ
- String constants that may have changed
- Configuration data that might be build-specific

### Segment Analysis
The warning about segment offset 0x10000 indicates the tool is working with DOS memory segments. This is normal behavior and doesn't indicate an error.

## Quick Reference: Debug Message Meanings

| Message | Meaning | Action Required |
|---------|---------|-----------------|
| `Dumping visited map` | Code analysis complete | None |
| `Unable to find segment` | Memory layout warning | Usually none |
| `DATA MISMATCH DETECTED` | Actual difference found | Investigate specific location |
| `VERIFICATION SUCCESS` | All data matches | None |
| `VERIFICATION FAILED` | Differences exist | Use detailed output to locate issues |