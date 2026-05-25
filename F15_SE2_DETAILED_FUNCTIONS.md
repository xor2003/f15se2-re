# F-15 Strike Eagle II Detailed Function Documentation

## Mathematical Utilities (SUPPORT.C)

### Range Functions
- **`rng(int val, int min, int max)`** - Clamps a value within specified range
- **`rng2(int val, int min, int max)`** - Alternative range clamping with different boundary handling

### Distance & Angle Functions
- **`xydist(int x1, int y1, int x2, int y2)`** - Calculates 2D distance between points
- **`uangle(int dx, int dy)`** - Calculates angle using ARCTAN lookup table
- **`sinX(int angle)`** - Sine function with 1024-unit circle scaling
- **`cosX(int angle)`** - Cosine function with 1024-unit circle scaling

### Utility Functions
- **`wrd(int val)`** - Converts value to 16-bit word
- **`sgn(int val)`** - Returns sign of value (-1, 0, 1)
- **`seedme(int seed)`** - Seeds random number generator
- **`seedme2(int seed)`** - Alternative seeding for second RNG
- **`rnd()`** - Returns random number (0-32767)
- **`rnd2()`** - Returns random number from second generator

### Timing
- **`WaitTicks(int ticks)`** - Waits specified VGA refresh ticks

## HUD Message System (MESSAGE.C)

### Core Message Functions
- **`Messages()`** - Main message processing loop
- **`Message(char *msg, int priority)`** - Adds message to queue
- **`MyMessages()`** - Displays queued messages on HUD
- **`MyMessage(char *msg)`** - Displays immediate message

### Message Display Functions
- **`MsgBox(int x, int y, int w, int h)`** - Draws message box
- **`MBox(int x, int y, int w, int h, int color)`** - Colored message box
- **`MsgPrnt(int x, int y, char *msg, int color)`** - Prints formatted message
- **`InSideMSGBox(int x, int y)`** - Checks if coordinates inside message box
- **`OutSideMSGBox(int x, int y)`** - Positions message box outside area
- **`OutSideHeading(int x, int y)`** - Displays heading/altitude info

## Joystick System (NJOYCAL.C)

### Configuration Functions
- **`SetJoysticks(int type)`** - Sets joystick type (0=none, 1=analog, 2=digital)
- **`GetJoyConfig()`** - Reads joystick configuration from JOY.F14
- **`SaveJoyConfig()`** - Saves configuration to JOY.F14

### Calibration Functions
- **`JoyRecal()`** - Interactive joystick calibration routine
- **`NShowJoy(int x, int y)`** - Displays joystick position visually
- **`NWaitShowJoy(int x, int y)`** - Shows joystick with delay

## Memory Management (util.c)

### DOS Memory Functions
- **`dos_allocmem(unsigned int paras)`** - Allocates DOS memory paragraphs
- **`dos_freemem(unsigned int seg)`** - Frees DOS memory segment
- **`dos_setblock(unsigned int paras, unsigned int seg)`** - Resizes memory block

### Far Pointer Operations
- **`dos_fmemcpy(void far *dest, void far *src, unsigned int n)`** - Far memory copy
- **`dos_fmemset(void far *dest, int c, unsigned int n)`** - Far memory set
- **`dos_fstrlen(char far *s)`** - Far string length
- **`dos_fstrcpy(char far *dest, char far *src)`** - Far string copy
- **`dos_fputs(char far *s, int fh)`** - Far string output to file

### File Operations
- **`dos_open(char *filename, int mode)`** - Opens file with DOS services
- **`dos_close(int fh)`** - Closes file handle
- **`dos_read(int fh, void *buffer, unsigned int count)`** - Reads from file
- **`dos_write(int fh, void *buffer, unsigned int count)`** - Writes to file
- **`dos_lseek(int fh, long offset, int origin)`** - Seeks file position

## Debugging System (debug.c)

### Logging Functions
- **`DebugLog(char *msg)`** - Logs message with timestamp
- **`DebugDump(void *buffer, int size, char *filename)`** - Dumps buffer to file
- **`DebugInit()`** - Initializes debug system
- **`DebugClose()`** - Closes debug output

### Utility Functions
- **`GetTimestamp()`** - Returns current system timestamp
- **`ChangeExtension(char *filename, char *newext)`** - Changes file extension

## Overlay System (overlay.c)

### Core Overlay Functions
- **`LoadOverlay(char *filename)`** - Loads overlay from file
- **`UnloadOverlay()`** - Unloads current overlay
- **`GetOverlayEntry(int index)`** - Gets function pointer from jump table

### Overlay Format
- **Header Structure**: Contains relocation information
- **Jump Table**: Function pointers for overlay entry points
- **Relocation**: Far call fixups for dynamic loading

## BIOS Functions (biosfunc.c)

### Keyboard Functions
- **`GetKeyFlags()`** - Reads keyboard flags from BIOS data area
- **`SetKeyFlags(int flags)`** - Sets keyboard flags
- **`WaitKey()`** - Waits for keypress

### System Functions
- **`GetSystemTime()`** - Reads BIOS time
- **`Reboot()`** - System reboot

## 3D Object System (3DOBJECT.C)

### Object Management
- **`Load3DObject(char *filename)`** - Loads 3D model from file
- **`Render3DObject(int obj_id, int x, int y, int z)`** - Renders 3D object
- **`Free3DObject(int obj_id)`** - Frees 3D object memory

### Transformation Functions
- **`Rotate3D(int obj_id, int x, int y, int z)`** - Rotates 3D object
- **`Scale3D(int obj_id, int scale)`** - Scales 3D object
- **`Project3D(int x, int y, int z)`** - 3D to 2D projection

## AWACS System (AWACS.C)

### Communication Functions
- **`AWACSContact(int type, int x, int y, int z)`** - Reports contact to AWACS
- **`AWACSWarning(int type, char *message)`** - Issues warning
- **`ProcessAWACS()`** - Main AWACS processing loop

### Voice Functions
- **`PlayVoice(int voice_id)`** - Plays voice message
- **`QueueVoice(int voice_id)`** - Queues voice for playback

## Flight Mathematics (FLTMATH.C)

### Flight Model Functions
- **`CalcLift(float speed, float angle)`** - Calculates lift force
- **`CalcDrag(float speed, float angle)`** - Calculates drag force
- **`UpdateFlightModel()`** - Updates aircraft physics
- **`ApplyControls(float pitch, float roll, float yaw)`** - Applies control inputs

### Navigation Functions
- **`CalcHeading(float dx, float dy)`** - Calculates heading
- **`CalcDistance(float x1, float y1, float x2, float y2)`** - Calculates distance
- **`UpdatePosition()`** - Updates aircraft position

## World System (wldparse.cpp)

### World Parsing
- **`ParseWorldFile(char *filename)`** - Parses world definition file
- **`LoadTerrain(int sector_x, int sector_y)`** - Loads terrain data
- **`GetElevation(float x, float y)`** - Gets ground elevation

### Object Placement
- **`PlaceObject(int type, float x, float y, float z)`** - Places world object
- **`RemoveObject(int id)`** - Removes world object
- **`UpdateObjects()`** - Updates all world objects

## Graphics System

### VGA Functions
- **`SetVideoMode(int mode)`** - Sets VGA video mode
- **`SetPalette(int index, int r, int g, int b)`** - Sets VGA palette
- **`ClearScreen()`** - Clears video memory
- **`DrawPixel(int x, int y, int color)`** - Draws pixel

### 3D Rendering
- **`DrawLine3D(int x1, int y1, int z1, int x2, int y2, int z2)`** - Draws 3D line
- **`DrawPolygon(int *points, int n_points)`** - Draws filled polygon
- **`TransformPoint(float x, float y, float z)`** - Transforms 3D point

## Audio System

### Sound Blaster Functions
- **`SBInit()`** - Initializes Sound Blaster
- **`SBPlaySample(char *sample, int length)`** - Plays digital sample
- **`SBSetVolume(int volume)`** - Sets master volume

### AdLib Functions
- **`AdLibInit()`** - Initializes AdLib
- **`AdLibPlayNote(int channel, int note, int velocity)`** - Plays musical note
- **`AdLibSetInstrument(int channel, int instrument)`** - Sets instrument

## Mission System

### Mission Loading
- **`LoadMission(char *filename)`** - Loads mission file
- **`ParseMissionData()`** - Parses mission objectives
- **`SetupMission()`** - Initializes mission state

### Objective Tracking
- **`CheckObjectives()`** - Checks mission objectives
- **`UpdateScore()`** - Updates mission score
- **`MissionComplete()`** - Handles mission completion

## Memory Organization

### Conventional Memory
- **Code Segment**: Main game code (64KB)
- **Data Segment**: Global variables and constants
- **Stack Segment**: Local variables and call stack

### Extended Memory
- **EMS Memory**: Message buffers, large data structures
- **Overlay Area**: Dynamic code loading (64KB blocks)
- **Video Memory**: VGA frame buffer (64KB)

## File Formats

### JOY.F14 Format
- **Header**: Joystick type and calibration data
- **Axes**: Min/max values for each axis
- **Buttons**: Button mapping and dead zones

### Mission Files
- **Header**: Mission name and objectives
- **Waypoints**: Navigation waypoints
- **Targets**: Enemy and friendly units
- **Weather**: Environmental conditions

## Performance Considerations

### Optimization Techniques
- **Fixed-point math**: Avoids floating point operations
- **Lookup tables**: Pre-calculated trigonometric values
- **Assembly routines**: Critical functions in assembly
- **Overlay system**: Manages memory constraints

### Memory Usage
- **Code**: ~400KB total (with overlays)
- **Data**: ~100KB for game state
- **Graphics**: ~200KB for sprites and textures
- **Audio**: ~50KB for sound buffers