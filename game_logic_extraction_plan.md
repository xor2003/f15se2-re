# Game Logic Extraction Plan - F-15 Strike Eagle II

## Overview
This plan documents the extraction and analysis of the core game logic from F-15 Strike Eagle II, focusing on the main game loop, input handling, and mission management systems.

## Game Logic Functions Identified

### Main Game Loop
| Function | Address Range | Purpose | Memory Segment |
|----------|---------------|---------|----------------|
| `main` | 0x0269-0x03B8 | Main game loop | seg000 |
| `otherKeyDispatch` | 0x03B9-0x04A8 | Input handling dispatcher | seg000 |

### Mission Logic Functions
| Function | Address Range | Purpose | Memory Segment |
|----------|---------------|---------|----------------|
| `sub_155AB` | 0x155AB-0x156E8 | Mission initialization | seg000 |
| `sub_18E50` | 0x18E50-0x18F3D | Mission state management | seg000 |

### Additional Game Logic
| Function | Address Range | Purpose | Memory Segment |
|----------|---------------|---------|----------------|
| `sub_1A2F0` | 0x1A2F0-0x1A3DD | Game state updates | seg000 |
| `sub_1B4A0` | 0x1B4A0-0x1B58D | Score/credit system | seg000 |

## Game Architecture Overview

### System Components
```
Game Logic Architecture:
├─ Main Game Loop: 0x0269-0x03B8 (335 bytes)
├─ Input Handling: 0x03B9-0x04A8 (239 bytes)
├─ Mission Logic: 0x155AB-0x156E8 (317 bytes)
├─ State Management: 0x18E50-0x18F3D (237 bytes)
└─ Score System: 0x1A2F0-0x1A3DD (237 bytes)
```

### Memory Organization
- **Code Segment**: seg000 (0x0000-0xF881)
- **Data Segment**: dseg (0x0000-0xA020)
- **BSS Segment**: dseg:0x66C0-0xA016 (uninitialized data)

## Game State Machine

### Main Game States
```c
typedef enum {
    GAME_STATE_INIT,        // Initialization
    GAME_STATE_MENU,        // Main menu
    GAME_STATE_BRIEFING,    // Mission briefing
    GAME_STATE_FLIGHT,      // In-flight
    GAME_STATE_COMBAT,      // Combat mode
    GAME_STATE_DEBRIEFING,  // Mission debriefing
    GAME_STATE_SCORE,       // Score display
    GAME_STATE_EXIT         // Game exit
} GameState;
```

### Input Handling System
```c
typedef struct {
    uint8_t key_states[256];    // Keyboard state array
    uint16_t mouse_x;           // Mouse X position
    uint16_t mouse_y;           // Mouse Y position
    uint8_t mouse_buttons;      // Mouse button states
    uint16_t joystick_x;        // Joystick X axis
    uint16_t joystick_y;        // Joystick Y axis
    uint8_t joystick_buttons;   // Joystick button states
} InputState;
```

## Extraction Process

### Step 1: Extract Main Game Loop
```bash
# Extract main game loop
./lst2asm -c conf/egame_rc.json -f main -o src/game/main.asm
./lst2ch -c conf/egame_rc.json -f main -o include/game/main.h
```

### Step 2: Extract Input Handling
```bash
# Extract input dispatcher
./lst2asm -c conf/egame_rc.json -f otherKeyDispatch -o src/game/otherKeyDispatch.asm
./lst2ch -c conf/egame_rc.json -f otherKeyDispatch -o include/game/otherKeyDispatch.h
```

### Step 3: Extract Mission Logic
```bash
# Extract mission initialization
./lst2asm -c conf/egame_rc.json -f sub_155AB -o src/game/mission_init.asm
./lst2ch -c conf/egame_rc.json -f sub_155AB -o include/game/mission_init.h

# Extract mission state management
./lst2asm -c conf/egame_rc.json -f sub_18E50 -o src/game/mission_state.asm
./lst2ch -c conf/egame_rc.json -f sub_18E50 -o include/game/mission_state.h
```

### Step 4: Extract Additional Logic
```bash
# Extract game state updates
./lst2asm -c conf/egame_rc.json -f sub_1A2F0 -o src/game/state_updates.asm
./lst2ch -c conf/egame_rc.json -f sub_1A2F0 -o include/game/state_updates.h

# Extract score system
./lst2asm -c conf/egame_rc.json -f sub_1B4A0 -o src/game/score_system.asm
./lst2ch -c conf/egame_rc.json -f sub_1B4A0 -o include/game/score_system.h
```

## Game Data Structures

### Mission Configuration
```c
typedef struct {
    char mission_name[32];      // Mission identifier
    uint8_t difficulty;         // Mission difficulty (1-5)
    uint16_t target_count;      // Number of targets
    uint32_t fuel_load;         // Starting fuel (lbs)
    uint16_t ammo_load;         // Ammunition count
    uint8_t weather_type;       // Weather conditions
    uint8_t time_of_day;        // Day/night mission
    uint32_t waypoints[10][2];  // X,Y coordinates for 10 waypoints
} MissionConfig;
```

### Aircraft State
```c
typedef struct {
    uint32_t x_pos;             // X coordinate (world units)
    uint32_t y_pos;             // Y coordinate (world units)
    uint32_t z_pos;             // Altitude (feet)
    uint16_t heading;           // Heading (degrees * 10)
    uint16_t speed;             // Airspeed (knots)
    uint16_t fuel;              // Remaining fuel (lbs)
    uint8_t  damage[8];         // Damage to 8 aircraft systems
    uint8_t  weapon_status[4];  // Status of 4 weapon types
} AircraftState;
```

### Target System
```c
typedef struct {
    uint32_t x_pos;             // X coordinate
    uint32_t y_pos;             // Y coordinate
    uint8_t  type;              // Target type (0-255)
    uint8_t  priority;          // Target priority (1-10)
    uint16_t hit_points;        // Damage required to destroy
    uint8_t  status;            // 0=active, 1=destroyed, 2=disabled
} TargetInfo;
```

## Input System Analysis

### Keyboard Mapping
```
Key Mapping:
├─ Arrow Keys: Aircraft control
│  ├─ Up: Pitch down
│  ├─ Down: Pitch up
│  ├─ Left: Roll left
│  └─ Right: Roll right
├─ Function Keys:
│  ├─ F1: Help
│  ├─ F2: Save game
│  ├─ F3: Load game
│  └─ F10: Exit
├─ Number Keys: Weapon selection
│  ├─ 1: Gun
│  ├─ 2: Missiles
│  ├─ 3: Bombs
│  └─ 4: ECM
└─ Space: Fire weapon
```

### Joystick Support
- **X-Axis**: Roll control (-32768 to 32767)
- **Y-Axis**: Pitch control (-32768 to 32767)
- **Button 0**: Fire weapon
- **Button 1**: Weapon select
- **Button 2**: ECM toggle

## Game Loop Analysis

### Main Loop Structure
```c
while (game_running) {
    // 1. Process input
    handle_keyboard_input();
    handle_joystick_input();
    
    // 2. Update game state
    update_aircraft_physics();
    update_weapons_system();
    update_targets();
    
    // 3. Render frame
    render_cockpit();
    render_outside_view();
    render_hud();
    
    // 4. Audio processing
    update_engine_sound();
    update_weapon_sounds();
    
    // 5. Check game conditions
    check_mission_complete();
    check_player_death();
    
    // 6. Frame timing
    wait_for_vsync();
}
```

### Timing System
- **Frame Rate**: 30 FPS (33.33ms per frame)
- **Physics Update**: 60 Hz (16.67ms)
- **Input Polling**: 120 Hz (8.33ms)
- **Audio Update**: 22050 Hz (45.35μs)

## Mission System

### Mission Types
1. **Air Superiority**: Destroy enemy aircraft
2. **Ground Attack**: Destroy ground targets
3. **Reconnaissance**: Photograph targets
4. **Escort**: Protect friendly aircraft
5. **Interception**: Stop enemy bombers

### Scoring System
```c
typedef struct {
    uint32_t total_score;       // Overall mission score
    uint32_t targets_destroyed; // Number of targets hit
    uint32_t accuracy;          // Hit percentage (0-100)
    uint32_t time_bonus;        // Bonus for fast completion
    uint32_t survival_bonus;    // Bonus for aircraft survival
    uint32_t fuel_bonus;        // Bonus for fuel efficiency
} MissionScore;
```

### Target Validation
- **Primary Targets**: Must be destroyed for mission success
- **Secondary Targets**: Optional, provide bonus points
- **Collateral Damage**: Penalty for hitting wrong targets
- **Time Limits**: Missions must be completed within time limit

## Build and Test

### Compilation
```bash
# Build game logic module
./dosbuild.sh src/game/game_logic.asm

# Build individual components
./dosbuild.sh src/game/main.asm
./dosbuild.sh src/game/otherKeyDispatch.asm
```

### Testing Framework
```bash
# Test game initialization
dosbox -c "mount c build" -c "c:" -c "main --test-init"

# Test input handling
dosbox -c "mount c build" -c "c:" -c "otherKeyDispatch --test-input"

# Test mission system
dosbox -c "mount c build" -c "c:" -c "mission_test --scenario=training"
```

## Debugging and Analysis

### Debug Features
- **Frame Counter**: Display current frame number
- **Position Display**: Show aircraft coordinates
- **State Monitor**: Display current game state
- **Input Logger**: Log all keyboard/joystick inputs
- **Performance Monitor**: Show frame timing

### Memory Inspection
```bash
# Dump game state
./lst2asm -c conf/egame_rc.json -f dump_game_state -o debug/game_state.asm

# Analyze memory usage
./lst2asm -c conf/egame_rc.json -f memory_analyzer -o debug/memory_map.asm
```

## Advanced Analysis

### Reverse Engineering Techniques
1. **Static Analysis**: Examine assembly code for logic flow
2. **Dynamic Analysis**: Use DOSBox debugger to trace execution
3. **Memory Analysis**: Monitor memory changes during gameplay
4. **Input Analysis**: Map game responses to user inputs

### Code Patterns
- **State Machines**: Look for switch/case patterns
- **Event Handlers**: Identify interrupt-driven code
- **Data Structures**: Map global variables to game objects
- **Timing Loops**: Identify frame timing and update cycles

## Modernization Considerations

### Portability Issues
- **DOS Interrupts**: Replace with modern OS APIs
- **Memory Access**: Convert from segment:offset to flat memory
- **Input Handling**: Replace BIOS keyboard/joystick calls
- **Graphics**: Convert from VGA to modern graphics APIs

### Enhancement Opportunities
- **Higher Resolution**: Support modern display resolutions
- **Better Input**: Add mouse support and customizable controls
- **Save States**: Implement modern save/load system
- **Multiplayer**: Add network multiplayer support

## Next Steps
1. Extract and document all game logic functions
2. Create comprehensive test suite for game mechanics
3. Map all game states and transitions
4. Document save/load system
5. Analyze AI behavior for enemy aircraft
6. Document weapon systems and ballistics