cmake_minimum_required(VERSION 3.20)

project(f15 LANGUAGES CXX)

set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Virtual-overlay gfx trampolines: start/end/egame far-call into f15.exe's
# gfx_impl.c at runtime. f15 itself links gfx_impl.c directly instead.
set(NOASM_GFX_SOURCES
    ${SRC_DIR}/slottram.c
    ${SRC_DIR}/ovlpatch.c
    ${SRC_DIR}/compat64/egregsh.c
)

# Shared gfx-slot / timer / misc / pic / overlay basics — the same C
# implementations every program's NO_ASM build routes its slots through.
set(SHARED_SLOT_SOURCES
    ${SRC_DIR}/shared/gfximpl.c
    ${SRC_DIR}/shared/miscimpl.c
    ${SRC_DIR}/shared/ovlimpl.c
    ${SRC_DIR}/shared/picimpl.c
    ${SRC_DIR}/shared/timer.c
)

# File + string helpers. egame provides its own (egfileio.c / egtacmap.c), so it
# omits these to avoid redefining openFileWrapper/closeFileWrapper/drawStringCentered.
set(SHARED_IO_SOURCES
    ${SRC_DIR}/shared/file_io.c
    ${SRC_DIR}/shared/cleanup.c
    ${SRC_DIR}/shared/drawstr.c
    ${SRC_DIR}/shared/textfmt.c
    ${SRC_DIR}/shared/filepic.c
)

set(SHARED_SOURCES
    ${SHARED_SLOT_SOURCES}
    ${SHARED_IO_SOURCES}
)

set(START_SOURCES
    ${SRC_DIR}/stmain.c
    ${SRC_DIR}/stinit.c
    ${SRC_DIR}/stmissn.c
    ${SRC_DIR}/stsprit.c
    ${SRC_DIR}/strand.c
    ${SRC_DIR}/stpilot.c
    ${SRC_DIR}/stalloc.c
    ${SRC_DIR}/stterr.c
    ${SRC_DIR}/stparse.c
    ${SRC_DIR}/stgen.c
    ${SRC_DIR}/stdata.c
    ${SHARED_SOURCES}
    ${NOASM_GFX_SOURCES}
)

set(EGAME_SOURCES
    ${SRC_DIR}/egmain.c
    ${SRC_DIR}/egsphere.c
    ${SRC_DIR}/egframe.c
    ${SRC_DIR}/eg3dview.c
    ${SRC_DIR}/eg3dproj.c
    ${SRC_DIR}/eg3dgrid.c
    ${SRC_DIR}/eg3dload.c
    ${SRC_DIR}/eg3dmap.c
    ${SRC_DIR}/eg3dvp.c
    ${SRC_DIR}/eg3dcam.c
    ${SRC_DIR}/egflight.c
    ${SRC_DIR}/egthreat.c
    ${SRC_DIR}/egcombat.c
    ${SRC_DIR}/egtacmap.c
    ${SRC_DIR}/egui.c
    ${SRC_DIR}/egtarget.c
    ${SRC_DIR}/egtgt2.c
    ${SRC_DIR}/egmath.c
    ${SRC_DIR}/egkeys.c
    ${SRC_DIR}/egfileio.c
    ${SRC_DIR}/egpic.c
    ${SRC_DIR}/egdata.c
    ${SRC_DIR}/egfarbuf.c
    ${SRC_DIR}/eg3dmath.c
    ${SRC_DIR}/eghudm.c
    ${SRC_DIR}/eghudr.c
    ${SRC_DIR}/eg3drast.c
    ${SRC_DIR}/egsys.c
    ${SRC_DIR}/egtick.c
    ${SRC_DIR}/eginput.c
    ${SRC_DIR}/egstubs.c
    ${SHARED_SLOT_SOURCES}
    ${NOASM_GFX_SOURCES}
)

set(END_SOURCES
    ${SRC_DIR}/enmain.c
    ${SRC_DIR}/enmisc.c
    ${SRC_DIR}/enworld.c
    ${SRC_DIR}/eninput.c
    ${SRC_DIR}/entext.c
    ${SRC_DIR}/enrand.c
    ${SRC_DIR}/enaward.c
    ${SRC_DIR}/enbrief.c
    ${SRC_DIR}/endbrf.c
    ${SRC_DIR}/enfile.c
    ${SRC_DIR}/endata.c
    ${SHARED_SOURCES}
    ${NOASM_GFX_SOURCES}
)

set(F15_SOURCES
    ${SRC_DIR}/f15.c
    ${SRC_DIR}/dosfunc.c
    ${SRC_DIR}/biosfunc.c
    ${SRC_DIR}/log.c
    ${SRC_DIR}/overlay.c
    ${SRC_DIR}/f15util.c
    ${SRC_DIR}/gfx_impl.c
    ${SRC_DIR}/compat64/gfx_regshim.c
)

add_executable(f15 ${F15_SOURCES})
add_executable(start ${START_SOURCES})
add_executable(egame ${EGAME_SOURCES})
add_executable(end ${END_SOURCES})
add_executable(fixed_math_tests
    ${CMAKE_CURRENT_SOURCE_DIR}/tests/fixed_math_tests.cpp
)
add_executable(original_fixed_math_compare_tests
    ${CMAKE_CURRENT_SOURCE_DIR}/tests/original_fixed_math_compare_tests.cpp
    ${SRC_DIR}/eg3dmath.c
    ${SRC_DIR}/eg3dproj.c
    ${SRC_DIR}/egmath.c
    ${SRC_DIR}/egflight.c
    ${SRC_DIR}/eg3drast.c
    ${SRC_DIR}/egthreat.c
    ${SRC_DIR}/egcombat.c
    ${SRC_DIR}/egtarget.c
    ${SRC_DIR}/egtgt2.c
    ${SRC_DIR}/egframe.c
    ${SRC_DIR}/eg3dcam.c
    ${SRC_DIR}/eg3dmap.c
    ${SRC_DIR}/egtacmap.c
    ${SRC_DIR}/egkeys.c
    ${SRC_DIR}/egmain.c
    ${SRC_DIR}/eghudm.c
    ${SRC_DIR}/egstubs.c
    ${SRC_DIR}/enmain.c
    ${SRC_DIR}/enmisc.c
    ${SRC_DIR}/enbrief.c
    ${SRC_DIR}/strand.c
    ${SRC_DIR}/stgen.c
    ${SRC_DIR}/stterr.c
    ${SRC_DIR}/stparse.c
    ${SRC_DIR}/shared/filepic.c
    ${SRC_DIR}/shared/miscimpl.c
    ${SRC_DIR}/shared/textfmt.c
)

# Treat .c files as C++17 (decompiled code uses C++ features)
function(configure_f15_target target_name)
    set_source_files_properties(${ARGN} PROPERTIES LANGUAGE CXX)

    target_include_directories(${target_name} BEFORE PRIVATE
        ${SRC_DIR}/compat64
        ${SRC_DIR}
        ${SRC_DIR}/shared
    )

    target_compile_definitions(${target_name} PRIVATE BUGFIX NO_ASM)
    target_compile_features(${target_name} PRIVATE cxx_std_17)

    if(
        CMAKE_CXX_COMPILER_ID STREQUAL "GNU"
        OR
        (
            CMAKE_CXX_COMPILER_ID MATCHES "Clang"
            AND
            NOT CMAKE_CXX_COMPILER_FRONTEND_VARIANT STREQUAL "MSVC"
        )
    )
        target_compile_options(${target_name} PRIVATE
            -Wall

            -Wno-unused
            -Wno-unused-variable
            -Wno-unused-parameter
            -Wno-unused-function
            -Wno-unused-but-set-variable
            -Wno-deprecated-declarations
            -Wno-deprecated

            $<$<CXX_COMPILER_ID:Clang>:-ferror-limit=1000>
            $<$<CXX_COMPILER_ID:AppleClang>:-ferror-limit=1000>
            $<$<CXX_COMPILER_ID:GNU>:-fmax-errors=1000>

            -Wno-narrowing
        )

    elseif(
        MSVC
        OR
        CMAKE_CXX_COMPILER_FRONTEND_VARIANT STREQUAL "MSVC"
    )
        target_compile_options(${target_name} PRIVATE
            /nologo
            /TP
            /W3
            /wd4100  # unreferenced formal parameter
            /wd4101  # unreferenced local variable
            /wd4189  # local variable initialized but not referenced
            /wd4996  # deprecated / unsafe CRT
            /wd4244  # conversion, possible loss of data
            /wd4267  # size_t -> smaller type
            /wd4305  # truncation
            /wd4311  # pointer truncation
            /wd4312  # conversion to pointer of greater size
        )

    else()
        message(WARNING "Unknown C++ compiler: ${CMAKE_CXX_COMPILER_ID}")
    endif()
endfunction()

configure_f15_target(f15 ${F15_SOURCES})
configure_f15_target(start ${START_SOURCES})
configure_f15_target(egame ${EGAME_SOURCES})
configure_f15_target(end ${END_SOURCES})

target_compile_definitions(f15 PRIVATE DEBUG)

target_include_directories(fixed_math_tests PRIVATE ${SRC_DIR})
target_compile_features(fixed_math_tests PRIVATE cxx_std_17)
target_include_directories(original_fixed_math_compare_tests PRIVATE
    ${SRC_DIR}
    ${SRC_DIR}/compat64
)
target_compile_features(original_fixed_math_compare_tests PRIVATE cxx_std_17)
target_compile_definitions(original_fixed_math_compare_tests PRIVATE BUGFIX NO_ASM)
set_source_files_properties(
    ${SRC_DIR}/eg3dmath.c
    ${SRC_DIR}/eg3dproj.c
    ${SRC_DIR}/egmath.c
    ${SRC_DIR}/egflight.c
    ${SRC_DIR}/eg3drast.c
    ${SRC_DIR}/egthreat.c
    ${SRC_DIR}/egcombat.c
    ${SRC_DIR}/egtarget.c
    ${SRC_DIR}/egtgt2.c
    ${SRC_DIR}/egframe.c
    ${SRC_DIR}/eg3dcam.c
    ${SRC_DIR}/eg3dmap.c
    ${SRC_DIR}/egtacmap.c
    ${SRC_DIR}/egkeys.c
    ${SRC_DIR}/egmain.c
    ${SRC_DIR}/eghudm.c
    ${SRC_DIR}/egstubs.c
    ${SRC_DIR}/enmain.c
    ${SRC_DIR}/enmisc.c
    ${SRC_DIR}/enbrief.c
    ${SRC_DIR}/strand.c
    ${SRC_DIR}/stgen.c
    ${SRC_DIR}/stterr.c
    ${SRC_DIR}/stparse.c
    ${SRC_DIR}/shared/filepic.c
    ${SRC_DIR}/shared/miscimpl.c
    ${SRC_DIR}/shared/textfmt.c
    PROPERTIES LANGUAGE CXX
)
set_source_files_properties(${SRC_DIR}/eg3dmath.c PROPERTIES COMPILE_DEFINITIONS
    "sine=original_sine;cosine=original_cosine;fixedMulQ14=original_fixedMulQ14;shiftLongLeftInPlace=original_shiftLongLeftInPlace;shiftLongRightInPlace=original_shiftLongRightInPlace"
)
set_source_files_properties(${SRC_DIR}/eg3dproj.c PROPERTIES COMPILE_DEFINITIONS
    "scaleCoordToLod=original_scaleCoordToLod"
)
set_source_files_properties(${SRC_DIR}/egmath.c PROPERTIES COMPILE_DEFINITIONS
    "fixedMulQ14=original_fixedMulQ14;sine=original_sine;cosine=original_cosine;clampRange=original_clampRange;clampValue=original_clampValue;rangeApprox=original_rangeApprox;computeBearing=original_computeBearing;sinMul=original_sinMul;cosMul=original_cosMul;signOf=original_signOf;randomRange=original_randomRange;readAxisInput=original_readAxisInput;shapeDataOffset=original_shapeDataOffset"
)
set_source_files_properties(${SRC_DIR}/egflight.c PROPERTIES COMPILE_DEFINITIONS
    "UpdateThrottleState=original_UpdateThrottleState;applyRotationDelta=original_applyRotationDelta;computeAttitudeAngles=original_computeAttitudeAngles;fixedMulQ14=original_fixedMulQ14;sine=original_sine;cosine=original_cosine;clampRange=original_clampRange;clampValue=original_clampValue;rangeApprox=original_rangeApprox;computeBearing=original_computeBearing;signOf=original_signOf;randomRange=original_randomRange;signedRatio16=original_signedRatio16;valueToAngle=original_valueToAngle;complementAngle=original_complementAngle;isqrt=original_isqrt"
)
set_source_files_properties(${SRC_DIR}/egtarget.c PROPERTIES COMPILE_DEFINITIONS
    "buildRangeString=original_buildRangeString"
)
set_source_files_properties(${SRC_DIR}/egthreat.c PROPERTIES COMPILE_DEFINITIONS
    "computeThreatRangeBearing=original_computeThreatRangeBearing;computeThreatScore=original_computeThreatScore"
)
set_source_files_properties(${SRC_DIR}/egcombat.c PROPERTIES COMPILE_DEFINITIONS
    "bombTarget=original_bombTarget;samCanAcquireTarget=original_samCanAcquireTarget"
)
set_source_files_properties(${SRC_DIR}/egtgt2.c PROPERTIES COMPILE_DEFINITIONS
    "computeLoftAngle=original_computeLoftAngle;computeMapTargetRange=original_computeMapTargetRange;computeSimObjectRange=original_computeSimObjectRange;computeTargetBearing=original_computeTargetBearing;findWaypointEntry=original_findWaypointEntry;getTargetSymbol=original_getTargetSymbol;isTargetOverWater=original_isTargetOverWater;rotateVectorComponent=original_rotateVectorComponent;fixedMulQ14=original_fixedMulQ14;rangeApprox=original_rangeApprox;computeBearing=original_computeBearing"
)
set_source_files_properties(${SRC_DIR}/egframe.c PROPERTIES COMPILE_DEFINITIONS
    "appendMapEvent=original_appendMapEvent;applyGravityFall=original_applyGravityFall;countermeasures=original_countermeasures;drawWeaponSelectMarker=original_drawWeaponSelectMarker;resetSimObjectLocks=original_resetSimObjectLocks;scheduleEventCheck=original_scheduleEventCheck;scheduleTimedEvent=original_scheduleTimedEvent;tickMessageTimers=original_tickMessageTimers;updateBulletsAndFire=original_updateBulletsAndFire;updateTracerParticles=original_updateTracerParticles"
)
set_source_files_properties(${SRC_DIR}/eg3dcam.c PROPERTIES COMPILE_DEFINITIONS
    "setViewPosition=original_setViewPosition"
)
set_source_files_properties(${SRC_DIR}/eghudm.c PROPERTIES COMPILE_DEFINITIONS
    "hudSine=original_hudSine;hudPitchScale=original_hudPitchScale;drawClipLineGlobal=original_drawClipLineGlobal;hudComplex=original_hudComplex;hudRotateLadder=original_hudRotateLadder"
)
set_source_files_properties(${SRC_DIR}/egstubs.c PROPERTIES COMPILE_DEFINITIONS
    "drawCenteredLabelBox=original_drawCenteredLabelBox"
)
set_source_files_properties(${SRC_DIR}/enmain.c PROPERTIES COMPILE_DEFINITIONS
    "main=original_end_main;end_main=original_end_main;checkQuitFlag=original_checkQuitFlag"
)
set_source_files_properties(${SRC_DIR}/enmisc.c PROPERTIES COMPILE_DEFINITIONS
    "setupWorldBufPtr=original_setupWorldBufPtr"
)
set_source_files_properties(${SRC_DIR}/eg3dmap.c PROPERTIES COMPILE_DEFINITIONS
    "addTileEntry=original_addTileEntry;aspectScaleY=original_aspectScaleY;buildVertexSignMask=original_buildVertexSignMask;computeTileBounds=original_computeTileBounds;lookupTileEntry=original_lookupTileEntry;worldToTileIndex=original_worldToTileIndex"
)
set_source_files_properties(${SRC_DIR}/egtacmap.c PROPERTIES COMPILE_DEFINITIONS
    "mapXToScreen=original_mapXToScreen;mapYToScreen=original_mapYToScreen;objectToScreen=original_objectToScreen;plotMapObject=original_plotMapObject;setDrawColor=original_setDrawColor;tempStrcpy=original_tempStrcpy;setTimedMessage=original_setTimedMessage"
)
set_source_files_properties(${SRC_DIR}/egkeys.c PROPERTIES COMPILE_DEFINITIONS
    "exitSlowMotion=original_exitSlowMotion;makeSound=original_egkeys_makeSound;recalcTimeScale=original_recalcTimeScale;selectMissile=original_selectMissile"
)
set_source_files_properties(${SRC_DIR}/egmain.c PROPERTIES COMPILE_DEFINITIONS
    "main=original_egame_main;egame_main=original_egame_main;doNothing3=original_doNothing3;doNothing4=original_doNothing4"
)
set_source_files_properties(${SRC_DIR}/enbrief.c PROPERTIES COMPILE_DEFINITIONS
    "mapToScreenX=original_mapToScreenX;mapToScreenY=original_mapToScreenY;isPointInRect=original_isPointInRect;formatFlightTime=original_formatFlightTime;computeMissionResult=original_computeMissionResult;calcMissionScore=original_calcMissionScore"
)
set_source_files_properties(${SRC_DIR}/strand.c PROPERTIES COMPILE_DEFINITIONS
    "randMul=original_randMul;seedRandom=original_startSeedRandom"
)
set_source_files_properties(${SRC_DIR}/stgen.c PROPERTIES COMPILE_DEFINITIONS
    "approxDistance=original_approxDistance;itemDistance=original_itemDistance;positionUnit=original_positionUnit;setMoveDstComm7A=original_setMoveDstComm7A;getItemCoordStr=original_getItemCoordStr;formatGridRef=original_formatGridRef;calcBearing=original_calcBearing;clampValue=original_startClampValue;buildTargetLabel=original_buildTargetLabel;doNothing=original_doNothing"
)
set_source_files_properties(${SRC_DIR}/stterr.c PROPERTIES COMPILE_DEFINITIONS
    "scaleCoordByLevel=original_scaleCoordByLevel;lookupGridCell=original_lookupGridCell"
)
set_source_files_properties(${SRC_DIR}/stparse.c PROPERTIES COMPILE_DEFINITIONS
    "replaceExtension=original_replaceExtension"
)
set_source_files_properties(${SRC_DIR}/shared/filepic.c PROPERTIES COMPILE_DEFINITIONS
    "mystrcpy=original_mystrcpy"
)
set_source_files_properties(${SRC_DIR}/shared/miscimpl.c PROPERTIES COMPILE_DEFINITIONS
    "installCBreakHandler=original_installCBreakHandler;restoreCbreakHandler=original_restoreCbreakHandler;mystrcat=original_mystrcat;mystrlen=original_mystrlen;nearmemset=original_nearmemset"
)
set_source_files_properties(${SRC_DIR}/shared/textfmt.c PROPERTIES COMPILE_DEFINITIONS
    "drawStringCentered=original_sharedDrawStringCentered;stringWidth=original_stringWidth;my_ltoa=original_my_ltoa;my_itoa=original_my_itoa"
)
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    target_compile_options(original_fixed_math_compare_tests PRIVATE -ffunction-sections -fdata-sections)
    target_link_options(original_fixed_math_compare_tests PRIVATE -Wl,--gc-sections)
endif()

enable_testing()
add_test(NAME fixed_math_tests COMMAND fixed_math_tests)
add_test(NAME original_fixed_math_compare_tests COMMAND original_fixed_math_compare_tests)
add_test(NAME original_binary_function_harness
    COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/mzretools/original_binary_function_harness.py
)
