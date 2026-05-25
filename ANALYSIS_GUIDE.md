# F-15 Strike Eagle II Reverse Engineering Analysis Guide

## Overview
This guide documents the analysis engine used for reverse engineering F-15 Strike Eagle II DOS executables. The system provides sophisticated tools for analyzing, comparing, and understanding 16-bit DOS executables through instruction-level analysis.

## Core Analysis Engine

### 1. VariantMap System
**Location:** [`analysis.cpp:38-137`](mzretools/src/analysis.cpp:38)

The `VariantMap` class manages instruction variant relationships for identifying equivalent instruction sequences across different executables.

**Key Methods:**
- [`VariantMap::checkMatch()`](mzretools/src/analysis.cpp:55): Determines if two instruction sequences are variants
- [`VariantMap::find()`](mzretools/src/analysis.cpp:92): Searches for matching variants within buckets
- [`VariantMap::loadFromStream()`](mzretools/src/analysis.cpp:118): Loads variant mappings from configuration files

**Configuration Format:**
```
instruction1/instruction2/instruction3
```

### 2. CPU State Simulation
**Location:** [`analysis.cpp:139-253`](mzretools/src/analysis.cpp:139)

Implements a simplified CPU emulator for tracking register states during analysis.

**Key Functions:**
- [`applyMov()`](mzretools/src/analysis.cpp:139): Handles MOV instruction simulation
- [`applyPush()`](mzretools/src/analysis.cpp:211): Simulates PUSH operations
- [`applyPop()`](mzretools/src/analysis.cpp:231): Simulates POP operations

**Features:**
- Tracks register values through instruction execution
- Handles immediate, register-to-register, and memory-to-register moves
- Manages stack operations with push/pop tracking
- Creates segment mappings for DS, ES, and SS registers

### 3. Instruction Comparison System
**Location:** [`analysis.cpp:257-285`](mzretools/src/analysis.cpp:257)

Provides detailed comparison between instructions with multiple match levels.

**Match Types:**
- `INS_MATCH_FULL`: Complete instruction match
- `INS_MATCH_DIFF`: Different mapping but equivalent
- `INS_MATCH_DIFFOP1`: Different first operand
- `INS_MATCH_DIFFOP2`: Different second operand
- `INS_MATCH_MISMATCH`: No match

### 4. Duplicate Detection Engine
**Location:** [`analysis.cpp:1529-1617`](mzretools/src/analysis.cpp:1529)

Implements sophisticated duplicate routine detection using signature-based matching.

**Process:**
1. Generates signatures for reference routines
2. Searches for matching routines in target executables
3. Handles collision detection when routines match multiple signatures
4. Provides detailed statistics on duplicate detection rates

### 5. Data Reference Finder
**Location:** [`analysis.cpp:1620-1699`](mzretools/src/analysis.cpp:1620)

Brute-force search for potential variable references in executable data segments.

**Functionality:**
- Scans data segments for values matching known variable addresses
- Provides reference counting and sorting
- Identifies potential false positives based on reference frequency

## Data Structures

### Address System
**Location:** [`address.h`](mzretools/include/dos/address.h)

**Key Structures:**
- `Address`: Represents segmented addresses (segment:offset)
- `Block`: Represents address ranges for routines and memory regions
- `Segment`: Manages memory segments with bounds checking

**Constants:**
- `MEMORY_SIZE = 1_MB`: Total addressable memory
- `SEGMENT_SIZE = 64_kB`: Size of each segment
- `SEGMENT_MASK = 0xFFFF`: Segment boundary mask

### Routine Management
**Location:** [`routine.h`](mzretools/include/dos/routine.h)

**Key Structures:**
- `Routine`: Contains routine metadata including extents, reachable/unreachable blocks
- `RoutineEntrypoint`: Represents routine entry points with collision detection

**Features:**
- Collision detection between routines
- Block management for memory regions
- Extent calculation for routine boundaries

## Verification Process

### 1. Binary Comparison
The verification process uses the `mzdiff` tool to compare reconstructed binaries against references.

**Command Format:**
```bash
mzdiff --codemap map/egame.map --target build/EGAME.EXE --pattern [558bec83ec??c746] --entry 0x10 bin/egame.exe
```

### 2. Debug Output Analysis
**Common Debug Messages:**

- **"WARNING: Unable to find segment for offset 0x10000"**
  - Indicates the analysis tool cannot locate which segment contains offset 0x10000
  - Usually occurs when the offset exceeds segment boundaries

- **"Code map generation: 126 routines across 2 segments"**
  - Shows successful identification of routines across memory segments
  - Indicates partial success in code analysis

- **"Comparison result: mismatch"**
  - The reconstructed binary does not match the reference
  - Indicates differences in implementation or compilation

### 3. Verification Parameters
- **routineSizeThresh**: Minimum routine size (15 instructions)
- **routineDistanceThresh**: Distance threshold for routine matching (10% ratio)
- **entryPoint**: Starting address for analysis (0x10)

## Usage Patterns

### Typical Analysis Flow
1. Load target executable using `Executable` class
2. Generate routine signatures from reference executable
3. Use `findDuplicates()` to identify matching routines
4. Apply `findDataRefs()` to locate variable references
5. Use CPU state simulation for register tracking during analysis

### Configuration Files
- **Variant mappings**: Text files with slash-separated variant definitions
- **Debug output**: Controlled via `OUTPUT_CONF(LOG_ANALYSIS)` macro
- **Distance thresholds**: Configurable for duplicate detection

## Security Considerations
- Uses `Security::safeRead16()` for safe memory access
- Validates segment boundaries before memory access
- Handles edge cases in segment boundary calculations

## Performance Characteristics
- Brute-force data reference search is O(n*m) where n=segment size, m=variable count
- Duplicate detection uses edit distance calculations for signature matching
- CPU simulation provides linear-time instruction processing

## Example Usage

### Basic Analysis
```cpp
// Load executable
Executable exe("EGAME.EXE");

// Create analyzer
Analyzer analyzer(exe);

// Find duplicates against reference
auto results = analyzer.findDuplicates(referenceExe);

// Find data references
auto refs = analyzer.findDataRefs();
```

### Custom Configuration
```cpp
// Set verification parameters
analyzer.setRoutineSizeThreshold(15);
analyzer.setRoutineDistanceThreshold(0.1);

// Load custom variant mappings
VariantMap variants;
variants.loadFromStream(configFile);
```

## Troubleshooting

### Common Issues
1. **Segment mapping failures**: Check segment boundaries and offset calculations
2. **Routine matching failures**: Adjust distance thresholds or variant mappings
3. **Memory access violations**: Verify segment permissions and boundaries

### Debug Tools
- Enable detailed logging with `OUTPUT_CONF(LOG_ANALYSIS)`
- Use `findDataRefs()` to identify potential variable locations
- Check routine signatures with `findDuplicates()` statistics

## File Structure
- `analysis.cpp`: Core analysis engine implementation
- `address.h`: Address and segment management
- `routine.h`: Routine and memory region management
- `codemap.cpp`: Code map generation and routine identification
- `security.h`: Safe memory access utilities