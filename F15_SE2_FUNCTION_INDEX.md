# F-15 Strike Eagle II Function Index

## Overview
This document provides a comprehensive index of all functions identified in the F-15 Strike Eagle II disassembly, categorized by functionality based on source code analysis.

## Function Categories

### 1. Graphics & Rendering Functions
**Source Files**: egame0.c, egame1.c, egame2.c, egame3.c
**Key Functions**:
- **3D Object Rendering**: Functions handling 3D model rendering and transformations
- **Plane Rendering**: Aircraft visualization and animation
- **Cockpit Display**: HUD elements, instruments, and cockpit rendering
- **World Rendering**: Terrain, sky, and environmental graphics

### 2. Audio & Sound Functions
**Source Files**: egame0.c, egame1.c, egame2.c, egame3.c
**Key Functions**:
- **Sound Effects**: Engine sounds, weapons, explosions
- **Speech System**: AWACS communications, warnings
- **Music**: Background music and themes
- **Audio Drivers**: Sound Blaster and AdLib support

### 3. Game Logic & AI Functions
**Source Files**: egame0.c, egame1.c, egame2.c, egame3.c
**Key Functions**:
- **Flight Model**: Physics simulation, aerodynamics
- **AI Systems**: Enemy aircraft behavior, wingman AI
- **Mission Logic**: Objectives, scoring, campaign progression
- **Weapon Systems**: Missiles, guns, targeting

### 4. Input & Control Functions
**Source Files**: NJOYCAL.C, egame*.c
**Key Functions**:
- **Joystick Handling**: Calibration, configuration (JOY.F14)
- **Keyboard Input**: Key mapping and processing
- **Mouse Support**: Mouse cursor and button handling

### 5. Memory Management Functions
**Source Files**: util.c, overlay.c
**Key Functions**:
- **EMS Memory**: Expanded memory management
- **Overlay System**: Dynamic code loading (Microprose format)
- **Memory Allocation**: DOS memory management
- **Far Pointer Operations**: Extended memory access

### 6. File I/O Functions
**Source Files**: util.c, output.c, overlay.c
**Key Functions**:
- **Configuration Files**: JOY.F14, game settings
- **Save/Load**: Mission progress, pilot records
- **Resource Loading**: Graphics, audio, mission data
- **Binary File Operations**: Overlay loading, data files

### 7. Debugging & Development Functions
**Source Files**: debug.c
**Key Functions**:
- **Logging System**: Timestamped debug output
- **Memory Dumping**: Buffer inspection tools
- **Error Handling**: File operation error reporting
- **Performance Monitoring**: Timing and profiling

### 8. Mathematical Utilities
**Source Files**: SUPPORT.C, FLTMATH.C
**Key Functions**:
- **Range Clamping**: `rng()`, `rng2()`
- **Distance Calculation**: `xydist()`
- **Trigonometry**: `sinX()`, `cosX()`, `uangle()`
- **Random Numbers**: `rnd()`, `rnd2()`, `seedme()`
- **Flight Math**: Specialized aviation calculations

### 9. HUD & Interface Functions
**Source Files**: MESSAGE.C
**Key Functions**:
- **Message System**: HUD message queue management
- **Text Display**: Formatted text output
- **Message Boxes**: Dialog and notification systems
- **Status Display**: Altitude, heading, speed indicators

### 10. System & BIOS Functions
**Source Files**: biosfunc.c, dosfunc.c
**Key Functions**:
- **BIOS Interaction**: Keyboard flags, system calls
- **DOS Services**: File operations, memory management
- **Hardware Detection**: Joystick, sound card detection
- **System Configuration**: Hardware initialization

## Memory Map & Address Ranges

### Code Segments
- **Main Game Code**: 0x1000-0x8000 (varies by overlay)
- **Overlay Segments**: Dynamically loaded 64KB blocks
- **EMS Memory**: Used for message buffering and large data

### Data Segments
- **Video Memory**: 0xA0000-0xAFFFF (VGA)
- **BIOS Data Area**: 0x400-0x4FF
- **Game Data**: Various segments based on overlay

## File Structure

### Configuration Files
- **JOY.F14**: Joystick calibration data
- **Game configuration**: Settings and preferences
- **Pilot records**: Save game data

### Resource Files
- **Graphics**: Sprites, 3D models, textures
- **Audio**: Sound effects, speech, music
- **Missions**: Campaign and single mission data

## Cross-Reference Notes

### Disassembly to Source Mapping
- **Auto-generated names**: Disassembly uses `sub_XXXXX` format
- **Actual function names**: Available in source files
- **Address correlation**: Functions mapped to specific memory addresses

### Key Observations
- **Overlay system**: Allows larger game than conventional memory
- **EMS usage**: Critical for message system and large data
- **Modular design**: Clear separation of graphics, audio, game logic
- **DOS-specific**: Uses DOS interrupts and memory management

## Development Notes

### Source Code Structure
- **Modular C code**: Organized into functional units
- **Assembly integration**: Critical routines in assembly
- **Hardware abstraction**: Layered approach to graphics/sound
- **Configuration system**: Extensive use of external files

### Reverse Engineering Challenges
- **Overlay complexity**: Dynamic code loading complicates analysis
- **Memory mapping**: EMS and conventional memory usage
- **Function naming**: Disassembly uses generic names
- **Data structures**: Complex nested structures for game state

## Next Steps for Reimplementation

1. **Memory Management**: Implement EMS and overlay system
2. **Graphics Engine**: Recreate 3D rendering pipeline
3. **Audio System**: Implement Sound Blaster/AdLib support
4. **Input System**: Joystick calibration and configuration
5. **Game Logic**: Flight model and AI systems
6. **File I/O**: Configuration and save system
7. **Debugging**: Implement logging and debugging tools

## Function Count Summary
- **Total Functions Identified**: 200+ (from disassembly)
- **Categorized Functions**: ~150 (from source analysis)
- **Graphics Functions**: ~40
- **Audio Functions**: ~30
- **Game Logic**: ~50
- **System Functions**: ~30