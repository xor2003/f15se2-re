#### **1. Game Logic, Naming Conventions, and Data Structures**

The documentation provides canonical names for game entities and describes their behavior, which must be used to name variables, functions, and data structures.

**1.1. Weapon Systems and OPFOR (Opposing Forces):**
The manuals and handbook detail the exact weapons available and the capabilities of enemy forces. This is a goldmine for defining data structures and verifying game constants.

*   **Player Weapon Data Points:**
    *   **AIM-120A AMRAAM:** Medium-range (Max: 36km, Effective: 16km), "fire-and-forget" radar-guided.
    *   **AIM-9M Sidewinder:** Short-range (Max: 18km, Effective: 9km), IR-homing, highly maneuverable.
    *   **AGM-65D/G Maverick:** Air-to-ground, "fire-and-forget." `Max. Number Carried: 6`, `Effective Range: 32 km`.
    *   **AIM-7M Sparrow:** `Max. Number Carried: 4`, `Effective Range: 44 km`, `Guidance: Semi-active radar homing`.
    *   **GBU-12 Paveway:** `Max. Number Carried: 8`, `Effective Range: 2 km per 1,000' of altitude`.
    *   **Mk 20 Rockeye II:** `Max. Number Carried: 4`, contains 247 bomblets.
    *   **AGM-88A HARM:** `Max. Number Carried: 4`, `Best Target: Ground radar stations`.

*   **Enemy Forces (OPFOR) Data Points:**
    *   **SAMs:** SA-2 (Beam-rider, Poor Maneuverability), SA-10/SA-12 (Doppler, Extreme Threat), Hawk (Doppler, Medium Threat), Rapier (Very Good Maneuverability, High Threat).
    *   **AAMs:** AA-2 Atoll (IR, Mild Threat), AA-10 Alamo (Active Doppler Radar, Extreme Threat).
    *   **Aircraft:** MiG-21 (Good Maneuverability), MiG-23 (Fair Maneuverability), MiG-29 (Excellent Maneuverability), F-4 Phantom (Fair Maneuverability).

*   **Agent Action:**
    1.  **Define Data Structures:** Immediately define C `structs` like `WeaponStats`, `SAM_Stats`, and `AircraftStats` to hold these fields. Use `enums` for categories like `GuidanceType` (e.g., `GUIDANCE_IR`, `GUIDANCE_SARH`, `GUIDANCE_DOPPLER`).
    2.  **Locate Data Tables:** Search the data segment of `EGAME.EXE` for arrays of constants that match these values (e.g., an array of SAM maneuverability ratings). This will locate the primary game data tables.
    3.  **Name Functions:** Any function that reads from these tables can now be accurately named (e.g., `getWeaponMaxCount()`, `getSAMThreatLevel()`).

**1.2. Mission Logic, Scoring, and Theaters:**
The manuals describe the exact menu flow, mission generation, and scoring logic.

*   **Menu Flow Logic:** The path to the new content is explicitly stated: `Theaters -> Other Areas -> [North Cape | Central Europe | Desert Storm]`. If `Desert Storm` is selected, the next options are `General Air Strikes` or `Historical Missions`.
*   **Historical Missions:** Eight specific, named missions are detailed (e.g., "Saddam's Eyes," "Scud Busting"). Each has a defined primary target type and weapon loadout.
*   **Scoring System:**
    *   **Base Scores:** `Enemy aircraft: 50`, `Primary target: 200`, `Secondary target: 100`.
    *   **Multipliers:** Scores are multiplied based on difficulty level (Rookie: x1, Pilot: x2, Veteran: x3, Ace: x4 for aircraft) and theater.
    *   **Penalties:** Crashing halves the score; a successful bailout results in 3/4 of the score.
*   **Promotions and Medals:**
    *   **Promotions:** `1st Lt.: 1,500 pts`, `Captain: 6,000 pts`, `Major: 12,000 pts`, etc. Bailing out three times ends a career.
    *   **Medals:** Awarded for single-mission scores. `Distinguished Flying Cross: 2,500 pts`, `Silver Star: 4,000 pts`, etc.

*   **Agent Action:**
    1.  **Map Menu Functions:** Use the menu flow to structure and name the functions in `START.EXE`. Search for string literals like "Other Areas" to find the relevant code.
    2.  **Reconstruct Scoring Logic:** Locate the functions that modify the player's score by searching for the base point constants (`50`, `100`, `200`). Reconstruct the promotion logic with a series of `if (player_score >= 6000) { player_rank = CAPTAIN; }`.
    3.  **Name World Data:** The names of cities and bases (`Murmansk`, `Baghdad`) provide the ground truth for naming data structures within the `.WLD` and `.3D*` files.

**1.3. Game Mechanics and AI:**
The documentation explains *how* specific systems work, which clarifies the purpose of complex code sections.

*   **Difficulty Levels:** Affects gun accuracy ("kill area" size), number and type of SAMs, enemy AI maneuvers, and damage tolerance.
*   **Missile Evasion:** Doppler-guided missiles (SA-10, SA-12, AA-10) cannot be fooled by chaff alone and require maneuvering to a perpendicular course. Beam-rider missiles (SA-2, SA-5) are easily fooled by chaff.
*   **Dogfighting Maneuvers:** The handbook provides a glossary of terms and detailed descriptions of maneuvers like the "Immelmann Turn," "Split-S," "Yo-Yo Turn," "jink," and "break turn."
*   **Afterburner Logic:** Used to regain energy in tight turns when stall warnings appear.

*   **Agent Action:**
    1.  **Identify State Flags:** Look for a global variable, `g_difficulty_level`, which will be used in `if` or `switch` statements to alter game parameters.
    2.  **Clarify AI Logic:** The missile evasion tactics directly explain the logic in the enemy AI and the player's warning systems. The code that checks the angle between the player and an incoming missile is the Doppler evasion logic.
    3.  **Name Flight Dynamics Code:** Use the glossary and maneuver descriptions to name functions and variables in `EGAME.EXE`'s flight model and AI code (e.g., `executeImmelmann()`, `calculateEnergyState()`).

---

#### **2. UI, HUD, and Input Mapping**

This information provides a direct bridge between user interaction, on-screen display, and the underlying code.

**2.1. Keyboard Map (Technical Supplement):**
This is a direct "cheat sheet" for the main input handling routine.

*   **Key Bindings:**
    *   `P`: `Pilot, Automatic on/off`
    *   `L`: `Landing Gear up/down`
    *   `S`, `M`, `G`: Arm Short, Medium, Ground missiles
    *   **`Alt/N`**: Toggles night condition (a new key from the scenario manual!)
    *   `Alt/D`: `Detail Adjust`
    *   `Alt/T`: `Training`

*   **Agent Action:**
    1.  **Locate the Keyboard Dispatcher:** Find the main input loop that checks for key presses.
    2.  **Name Functions:** The scan code for each key will be followed by a `call` or `jmp` to the corresponding function. This allows for immediate and accurate naming of dozens of functions: `toggleAutopilot()`, `toggleLandingGear()`, `armShortRangeMissile()`, etc.

**2.2. HUD and Cockpit Display Descriptions:**
The manual meticulously names every element on the screen.

*   **Named Elements:** "INS (Waypoint) Direction Indicator," "Stall Speed Indicator," "Vertical Velocity Indicator (VVI)," "Gunsight" (also called "pipper"), "Tracking Box."
*   **CRT Displays:** The three CRTs are explicitly named: "The Satellite Map" (left), "The Tactical Display" (center), and "Tracking Camera CRT" (right).
*   **Color Codes:** The technical supplement provides a table mapping colors to on-screen objects (e.g., on the Tactical Display, a "White airplane" is your F-15, a "Yellow plane" is at a higher altitude).

*   **Agent Action:**
    1.  **Name Rendering Functions:** Use these canonical names for the functions that render each specific HUD element (e.g., `drawWaypointIndicator()`, `renderPipper()`).
    2.  **Structure Cockpit Code:** The three main cockpit rendering functions can be named `renderSatelliteMap()`, `renderTacticalDisplay()`, and `renderTrackingCamera()`.
    3.  **Debug Graphics:** When analyzing the graphics code, the color values (e.g., `0x0E` for yellow) can be cross-referenced with this table to determine what object is being drawn.

---

#### **3. Technical Implementation Details**

The technical supplement provides low-level information that confirms implementation choices.

*   **Command-Line Switches:**
    *   `/J` (joystick), `/NJ` (no joystick)
    *   `/GM` (MCGA/VGA 256-color), `/GE` (EGA 16-color), etc.
    *   `/D0` - `/D3` (Detail levels)

*   **Agent Action:**
    1.  **Analyze `main()`:** This directly explains the argument parsing logic at the beginning of the game's `main()` function.
    2.  **Identify Global State Variables:** This confirms the existence and purpose of global variables like `g_joystick_enabled`, `g_graphics_mode`, and `g_detail_level`. Search for the code that sets these variables based on the command line.

*   **File Names:**
    *   The installation instructions for the F-19 scenarios explicitly list the required files: `NC.WLD`, `CE.3D3`, `CE.3DT`, `CEUROPE.SPR`, etc.

*   **Agent Action:**
    1.  **Confirm Asset Conventions:** This confirms the file naming convention and the different types of assets associated with each theater.
    2.  **Locate File Loaders:** Identify the functions responsible for loading each file type by searching for these string literals in the data segment.
