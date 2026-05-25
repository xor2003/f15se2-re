# Decompilation Guide
## Essential Microsoft C 5.1 Features for Binary-Identical Reconstruction

### 1. Memory Models (CL /A option)
```c
/Astring  // Custom model: 
          //   Code: s=small(near), l=large(far)
          //   Data: n=near, f=far, h=huge
          //   SS: d=(SS==DS), u=(SS!=DS, load DS), w=(SS!=DS, no load)

/AT       // Tiny:   code+data ≤64K (.COM file)
/AS       // Small:  code≤64K, data≤64K
/AM       // Medium: data≤64K, code>64K
/AC       // Compact: code≤64K, data>64K
/AL       // Large:  code>64K, data>64K
/AH       // Huge:   arrays >64K allowed
```

### 2. Critical Compiler Flags
```c
/Gs       // Disable stack probes (essential for small functions)
/Ot       // Favor speed over size optimization
/Od       // Disable all optimizations (for debugging)
/Zi       // Generate CodeView debug info
/Zc       // Case-sensitive _pascal handling
/J        // Default char is unsigned
```

### 3. Key Pragmas
Control low-level code generation:
```c
#pragma pack(1)      // Byte-aligned structs
#pragma check_pointer(on)  // Enable pointer checking
#pragma alloc_text(seg, func)  // Place function in specific segment
#pragma loop_opt(on) // Enable loop optimization
```

### 4. Calling Conventions
```c
/Gd  // Standard C: args pushed right-to-left, caller cleans
/Gr  // __fastcall: pass args in registers when possible
```

### 5. Data Type Sizes
| Type       | Size | Range               |
|------------|------|---------------------|
| char       | 1    | -128 to 127         |
| short      | 2    | -32,768 to 32,767   |
| long       | 4    | ±2.1e9              |
| float      | 4    | 1.2E-38 to 3.4E+38  |
| double     | 8    | 2.2E-308 to 1.8E+308|
| long double| 10   | 1.2E-4932 to 3.4E-4932 |

### 6. Compiler Idioms for Binary Matching
```c
// 32-bit shift (compiles to loop)
long l = 1;
l <<= 5;  // Generates: shl ax,1; rcl dx,1 (repeated)

// Branchless NULL check
result = (ptr != NULL);  // Compiles to: cmp ax,1; sbb cx,cx; neg cx

// Complex single-line expressions
if ((arr[i] = (fp = fopen(f)) == NULL)) count--;
```

### 7. Linker Options
```c
/Fm        // Generate map file
/Fe:EGAME  // Name output executable
/Fb        // Create bound executable (for DOS/OS2)
/STACK:0x2000  // Set stack size (hex)
```

### 8. Runtime Library Selection
```c
/FPi       // Inline 80x87 + emulator (default)
/FPc87     // 80x87 calls only (requires coprocessor)

```

#### Memory Segmentation
- Segment override prefixes for explicit segment selection
- Logical program structure through modular segments

#### Physical Address Calculation
- Physical address = (segment << 4) + offset
- 20-bit physical address space (1MB)

### 10. Compiler Flags from C5L.txt

#### Memory Models
```c
/AS       // Small model: code≤64K, data≤64K (default)
/AC       // Compact model: code≤64K, data>64K
/AM       // Medium model: data≤64K, code>64K
/AL       // Large model: code>64K, data>64K
```

#### Optimization Flags
```c
/O        // Enable optimization (same as /Ot)
/Oa       // Ignore aliasing
/Od       // Disable optimizations
/Oi       // Enable intrinsic functions
/Ol       // Enable loop optimizations
/On       // Disable "unsafe" optimizations
/Op       // Enable precision optimizations
/Or       // Disable in-line return
/Os       // Optimize for space
/Ot       // Optimize for speed (default)
/Ox       // Maximum optimization (/Oailt /Gs)
```

#### Code Generation
```c
/Gm       // Put strings in constant segment
/Gc       // Pascal-style function calls
/Gs       // Disable stack checking
/Gt[number] // Data size threshold
```

#### Stack Size Specification
```c
/F<hex>   // Set stack size in hex bytes (linker option)
```

### 11. Build Environment Setup

The original game was likely built with the following environment configuration:

#### Library Configuration
- Memory model: Small (default) - `SLIBCE.LIB`
- Floating point: Emulator library - `EM.LIB`
- Graphics: `GRAPHICS.LIB` for low-level rendering
- Standard libraries: `OLDNAMES.LIB` for compatibility

#### Environment Variables
```bash
INCLUDE=C:\C600\INCLUDE   # Header files
LIB=C:\C600\LIB           # Library files
HELPFILES=C:\C600\HELP\*.HLP  # Documentation
PATH=C:\C600\BIN;%PATH%   # Compiler tools
```

#### Compiler Invocation
```bash
CL /AS /Gs /Ot /Fe:EGAME.EXE *.c GRAPHICS.LIB
```

#### Key Configuration Files
1. `TOOLS.INI` - Contains compiler/linker settings
2. `NEW-VARS.BAT` - Sets environment variables
3. `CONFIG.SYS` - Includes `HIMEM.SYS` for extended memory

#### PWB (Programmer's WorkBench) Settings
- Debug option enabled for CodeView symbols
- Small memory model selected
- Floating point: Emulation
- Stack checking disabled (/Gs)

### 12. Key Library Functions

#### Graphics Functions
```c
_setvideomode(_MRES256COLOR);  // Set 320x200 256-color mode
_rectangle(_GBORDER, x1, y1, x2, y2);  // Draw rectangle outline
_setcolor(color);               // Set drawing color
_setvieworg(x, y);              // Set coordinate origin
```

#### Memory Management
```c
// Near heap allocation (default in small model)
char *buf = malloc(size);       // Allocate memory
free(buf);                      // Free memory

// Far heap allocation (for large data)
char far *fbuf = _fmalloc(size); // Allocate far memory
_ffree(fbuf);                   // Free far memory
```

#### File I/O
```c
FILE *fp = fopen("DATA.DAT", "rb");  // Open binary file
fread(buffer, 1, size, fp);          // Read data
fclose(fp);                          // Close file
```

#### Timing and Delays
```c
_sleep(milliseconds);  // Delay execution
```

#### Port I/O (Hardware Access)
```c
_outp(0x61, value);    // Write to port (sound, keyboard)
_inp(0x60);            // Read from port
```

### 13. Development Tools

#### Build Tools
- **CL.EXE**: Microsoft C 5.1 Compiler
  ```bash
  CL /AS /Gs /Ot /Fe:EGAME.EXE *.c GRAPHICS.LIB
  ```
- **LINK.EXE**: Segmented Executable Linker
  ```bash
  LINK /ST:8192 @EGAME.LNK
  ```
- **LIB.EXE**: Library Manager for creating custom libraries
- **MAKE/NMAKE**: Build automation (Makefile driven)

#### Debugging Tools
- **CodeView (CV.EXE)**: Source-level debugger
  ```bash
  CV /X EGAME.EXE  # Use extended memory
  ```
- **SYMDEB**: Symbolic debugger for low-level analysis

#### Utilities
- **EXEHDR**: Examine and modify .EXE headers
- **EXEMOD**: Modify .EXE file characteristics
- **MAPSYM**: Create symbol files for debugging
- **HELPMAKE**: Build custom help files

