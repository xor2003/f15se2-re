#include "fixed_math.hpp"
#include "comm.h"
#include "egtypes.h"
#include "endtypes.h"
#include "inttype.h"
#include "struct.h"

#include <dos.h>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <iostream>
#include <string>
#include <tuple>

using f15::fixed::Angle16;
using f15::fixed::Q15;
using namespace f15::fixed;

extern int original_sine(int angle);
extern int original_cosine(int angle);
extern int original_fixedMulQ14(int a, int b);
extern void original_shiftLongLeftInPlace(int count, long *ptr);
extern void original_shiftLongRightInPlace(int count, long *ptr);
extern int original_clampRange(int value, int minVal, int maxVal);
extern int original_clampValue(int value, int minVal, int maxVal);
extern int original_rangeApprox(int deltaX, int deltaY);
extern int original_computeBearing(int deltaX, int deltaY);
extern int original_sinMul(int angle, int value);
extern int original_cosMul(int angle, int value);
extern int original_signOf(int value);
extern int original_randomRange(int maxVal);
extern int original_readAxisInput(int axisIdx);
extern void original_UpdateThrottleState(void);
extern void original_applyRotationDelta(const int16 *matA, const int16 *matB);
extern void original_computeAttitudeAngles(void);
extern unsigned original_signedRatio16(int numerator, int denominator);
extern int original_valueToAngle(int value);
extern int original_complementAngle(int value);
extern int original_isqrt(int value);
extern int original_hudSine(int angle);
extern int original_hudPitchScale(int anglePitch);
extern int original_aspectScaleY(int screenY);
extern void original_addTileEntry(struct TileObject *rec, int value, char tag);
extern void original_buildVertexSignMask(int screenX, int screenY);
extern void original_computeTileBounds(int *minTileX, int *maxTileX, int *minTileY, int *maxTileY);
extern int original_lookupTileEntry(int lod, int subIndex, int tileX, int tileY);
extern void original_worldToTileIndex(int worldX, int worldY, int *outCol, int *outRow);
extern int original_mapToScreenX(unsigned char mapCoord);
extern int original_mapToScreenY(unsigned char mapCoord);
extern void original_setupWorldBufPtr(void);
extern char *original_formatFlightTime(int timeValue, char *buffer);
extern void original_computeMissionResult(void);
extern long original_calcMissionScore(int param);
extern int original_isPointInRect(const MenuItem *p);
extern int original_approxDistance(int dx, int dy);
extern int original_itemDistance(int idx1, int idx2);
extern void original_positionUnit(int unit, int loc);
extern char *original_getItemCoordStr(int16 idx);
extern char *original_formatGridRef(int16 wx, int16 wy, int16 theater);
extern int original_calcBearing(int dx, int dy);
extern int original_randMul(std::uint16_t maxVal);
extern void original_buildTargetLabel(int idx);
extern int original_mapXToScreen(int mapX);
extern int original_mapYToScreen(int mapY);
extern int original_objectToScreen(int mapX, int mapY, int16 *outScreenX, int16 *outScreenY);
extern int original_plotMapObject(int mapX, int mapY, int color, int big);
extern void original_setDrawColor(int color);
extern void original_tempStrcpy(const char *src);
extern void original_setTimedMessage(char *message);
extern int original_drawCenteredLabelBox(int panel, const char *text);
extern void original_buildRangeString(int rangeRaw);
extern int original_computeLoftAngle(void);
extern int original_computeMapTargetRange(int targetIdx);
extern int original_computeSimObjectRange(int objIdx);
extern int original_computeTargetBearing(int targetX, int targetY, int wantBearing);
extern int original_findWaypointEntry(int mapX, int mapY);
extern int original_computeThreatRangeBearing(int threatX, int threatY, int threatAlt, int threatType,
                                              int *outBearing, int *outRange);
extern int original_computeThreatScore(void);
extern int original_samCanAcquireTarget(int slot, int targetX, int targetY, int targetAlt, int mode);
extern void original_bombTarget(void);
extern int original_getTargetSymbol(int wpIdx);
extern int original_isTargetOverWater(int wpIdx);
extern long original_rotateVectorComponent(int axis, int vecX, int vecY, int vecZ);
extern void original_appendMapEvent(int eventType, int eventArg);
extern void original_applyGravityFall(void);
extern void original_countermeasures(int eventType);
extern void original_drawWeaponSelectMarker(int weaponIdx);
extern void original_resetSimObjectLocks(void);
extern void original_scheduleEventCheck(int eventObjIdx, unsigned int priority);
extern void original_scheduleTimedEvent(int keyVal, int delay);
extern void original_tickMessageTimers(void);
extern void original_updateBulletsAndFire(void);
extern void original_updateTracerParticles(void);
extern void original_exitSlowMotion(void);
extern void original_recalcTimeScale(void);
extern void original_selectMissile(void);
extern void original_setViewPosition(int viewX, int viewY, int viewZ);
extern std::uint32_t original_scaleCoordToLod(int level, std::uint32_t coord);
extern std::uint32_t original_scaleCoordByLevel(int level, std::uint32_t coord);
extern int original_lookupGridCell(int16 level, int16 col, int16 row);
extern int original_shapeDataOffset(int shapeId);
extern int original_setMoveDstComm7A(const char *filename, const char *mode);
extern void original_doNothing3(void);
extern void original_doNothing4(void);
extern void original_doNothing(std::FILE *handle);
extern void original_checkQuitFlag(void);
extern void original_installCBreakHandler(void);
extern void original_restoreCbreakHandler(void);
extern void original_replaceExtension(char *path, const char *source);
extern void original_mystrcpy(char *dest, const char *source);
extern void original_mystrcat(char *dst, const char *src);
extern int original_mystrlen(const char *s);
extern void original_nearmemset(void *dst, char val, int count);
extern void original_my_itoa(int value, char *buf);

namespace {

enum TestSamples : int {
    kRawAngleMax = 0xFFFF,
    kSignedWordMin = -32768,
    kSignedWordMinPlusOne = -32767,
    kSignedWordMax = 32767,
    kMapCoordShift = 7,
    kReadAxisRoll = 0,
    kReadAxisDisabled = 1,
    kReadAxisIgnoredAccum = 6,
    kReadAxisDisabledReturn = 0,
    kMapScaleX = 0x92,
    kMapScaleY = 0xC3,
    kNightMissionWeaponDataOffset = 0x6DA,
    kFormatFlightBaseTargetType = 0,
    kFormatFlightDayType = 1,
    kFormatFlightNightType = 4,
    kFormatFlightDayTime = 1830,
    kFormatFlightDayMiscBits = 1,
    kFormatFlightNightTime = 59,
    kFormatFlightNightMiscBits = 0,
    kFormatFlightForcedTime = 3600,
    kFormatFlightForcedMiscBits = 2,
    kMissionResultGridX = 8,
    kMissionResultGridY = 3,
    kMissionResultWorldCoordShift = 11,
    kMissionResultGridStride = 16,
    kMissionResultGridFlags = 0xA7,
    kMissionResultMask = 0x03,
    kCalcMissionRawWeaponCount = 20,
    kCalcMissionCappedWeaponCount = 15,
    kCalcMissionDifficulty = 2,
    kCalcMissionPrimaryAirUnit = 5,
    kCalcMissionPrimaryAirStatus = STATUS_PRIMARY_HIT | EVENT_AIR_KILL,
    kCalcMissionPrimaryAirScore = (kCalcMissionCappedWeaponCount * 25) + (kCalcMissionCappedWeaponCount * 200),
    kCalcMissionNoEventScore = 0,
    kCalcMissionCounterSentinel = 7,
    kItemDistanceFirstIndex = 0,
    kItemDistanceSecondIndex = 1,
    kItemDistanceFirstX = 1000,
    kItemDistanceFirstY = 2000,
    kItemDistanceSecondX = 700,
    kItemDistanceSecondY = 2600,
    kPositionUnitIndex = 1,
    kPositionUnitLocationIndex = 2,
    kPositionUnitPlaneType = 6,
    kPositionUnitInitialFlags = 0x0020,
    kPositionUnitWorldX = 1000,
    kPositionUnitWorldY = 2000,
    kPositionUnitLargeTargetFlag = 0x0200,
    kPositionUnitX = kPositionUnitWorldX + 9,
    kPositionUnitY = kPositionUnitWorldY - 12,
    kPositionUnitWorldCoordShift = 5,
    kPositionUnitAltitude = 140,
    kPositionUnitHeading = 0xFC00,
    kPositionUnitFlags = kPositionUnitInitialFlags | 0x0403,
    kPositionUnitMaxSpeed = 800,
    kPositionUnitRange = 520,
    kPositionUnitFuel = (kPositionUnitRange << 13) / kPositionUnitMaxSpeed,
    kSetMoveDstSuccess = 1,
    kWorldBufOffset = 0x7A,
    kFormatGridWorldObjectIndex = 2,
    kFormatGridWorldX = 0x2000,
    kFormatGridWorldY = 0x3000,
    kFormatGridTheaterCC = 5,
    kTargetLabelWorldObjectIndex = 0,
    kTargetLabelUnitRef = 2,
    kTargetLabelObjectIndex = 3,
    kTargetLabelTruncSentinel = 0x12,
    kReplaceExtensionPathBytes = 16,
    kMyStrcpyBufferBytes = 16,
    kLookupGridLevel4 = 4,
    kLookupGridLevel2 = 2,
    kLookupGridOutOfRangeCol = 4,
    kLookupGridDirectCol = 1,
    kLookupGridDirectRow = 2,
    kLookupGridDirectValue = 0x5A,
    kLookupGridNestedCol = 5,
    kLookupGridNestedRow = 6,
    kLookupGridParentIndex = 17,
    kLookupGridParentCell = 3,
    kLookupGridNestedIndex = 57,
    kLookupGridNestedValue = 0x6B,
    kLookupGridNotFound = -1,
    kAspectScaleShift = 2,
    kDynamicShapeFlag = 0x100,
    kShapeOffsetTableSlot = 0x7F,
    kAircraftModelSlotOffset = 0x92,
    kDynamicShapeSlotOffset = 0xC3,
    kRangeKmShift = 6,
    kRangeFractionMask = 0x3F,
    kMapRangeTargetIdx = 6,
    kWaypointLookupMapX = 128,
    kWaypointLookupMapY = 32640,
    kWaypointNotFound = -1,
    kThreatViewX = 0x2000,
    kThreatViewY = 0x3000,
    kThreatViewZ = 0x1000,
    kThreatMissionStatus = 1,
    kThreatX = 0x1C00,
    kThreatY = 0x3400,
    kThreatAltIgnored = 123,
    kThreatType = 4,
    kThreatLethality = 320,
    kThreatDangerTier = 7,
    kThreatEmptyType = 0,
    kThreatSentinelType = -1,
    kThreatAltitudeBase = 0x40,
    kThreatScoreBase = 3,
    kThreatMissionScale = 2,
    kThreatLethalityDivisor = 16,
    kThreatAltitudeShift = 6,
    kThreatAltitudeScoreShift = 7,
    kThreatScoreMissionStatus = 2,
    kThreatScoreTargetCount = 4,
    kThreatScoreType0 = 2,
    kThreatScoreType1 = 0,
    kThreatScoreType2 = 4,
    kThreatScoreType3 = 7,
    kThreatScoreDivisor = 64,
    kThreatScoreTotalDivisor = 100,
    kSamAcquireSlot = 0,
    kSamAcquireStartX = 1000,
    kSamAcquireStartY = 1000,
    kSamAcquireSpeed = 200,
    kSamAcquireHeadingEast = 0x4000,
    kSamAcquireTargetX = 1100,
    kSamAcquireTargetY = 1000,
    kSamAcquireTargetAltIgnored = 0,
    kSamAcquireModeForward = 0,
    kSamAcquireFrameRateScaling = 40,
    kSamAcquireExpectedRange = 100,
    kSamAcquireExpectedAim = 0x4000,
    kBombSuppressionFlag = 0x1000,
    kBombDamageMaskSentinel = 0x1234,
    kBombGunHitsSentinel = 0x55,
    kBombDamageTakenSentinel = 0,
    kDebriefHitX1 = 10,
    kDebriefHitY1 = 20,
    kDebriefHitX2 = 30,
    kDebriefHitY2 = 40,
    kDebriefCursorInsideX = 20,
    kDebriefCursorInsideY = 30,
    kDebriefCursorOutsideX = 40,
    kObjectMapCenterX = 0x2000,
    kObjectMapCenterY = 0x3000,
    kObjectScreenCenterX = 60,
    kObjectScreenCenterY = 140,
    kObjectClipRight = 200,
    kObjectClipBottom = 200,
    kPlotMapObjectHiddenColor = -1,
    kPlotMapObjectSmallMarker = 0,
    kPlotMapObjectHiddenResult = 1,
    kTacMapDrawColor = 0x1A,
    kTacMapFrameRateScaling = 4,
    kTacMapThreeSecondTimer = kTacMapFrameRateScaling * 3,
    kTargetIdentifiedFlag = 0x80,
    kTargetSymbolShapeIndex = 2,
    kWaterTargetCategory = 12,
    kLandTargetCategory = 7,
    kWaterTargetSymbol = 0x22,
    kLandTargetSymbol = 0x33,
    kIdentifiedSymbolBase = 0x100,
    kExplicitTargetSymbol = 0x155,
    kRotateVectorAxisX = 0,
    kRotateVectorHalfQ14 = 0x4000,
    kRotateVectorX = 3000,
    kRotateVectorY = -2000,
    kRotateVectorZ = 1000,
    kViewPositionX = 123,
    kViewPositionY = -456,
    kViewPositionZ = 789,
    kAttitudeIdentityDiagonal = 0x7FFF,
    kAttitudeProductDiagonal = 0x7FFE,
    kRotationDirtyCounterBefore = 7,
    kRotationDirtyCounterAfter = 8,
    kOrientationDirty = 1,
    kAttitudeValueToAngleZeroInput = 0,
    kThrottleHiddenHud = 0,
    kWorldTileViewCenterX = 100,
    kWorldTileViewCenterY = 50,
    kWorldTileMapOriginX = 120,
    kWorldTileMapOriginY = 90,
    kWorldTileSize = 16,
    kWorldTileWorldX = 140,
    kWorldTileWorldY = 80,
    kWorldTileOutCol = 10,
    kWorldTileOutRow = 8,
    kTileBoundsViewCenterX = 200,
    kTileBoundsViewCenterY = 160,
    kTileBoundsMapOriginX = 0,
    kTileBoundsMapOriginY = 0,
    kTileBoundsTileWorldSize = 16,
    kTileBoundsGridDim = 20,
    kTileBoundsClipMaxX = 319,
    kTileBoundsClipMaxY = 199,
    kTileBoundsMinX = 0,
    kTileBoundsMaxX = 7,
    kTileBoundsMinY = 0,
    kTileBoundsMaxY = 3,
    kAddTileInitialCount = 3,
    kAddTileLod = 2,
    kAddTileSubIndex = 5,
    kAddTileX = 7,
    kAddTileY = 9,
    kAddTileShapeOff = 0x1234,
    kAddTileFlag = 0x56,
    kAddTilePad = 0x5A,
    kAddTileSceneShape = 0x22,
    kAddTileSceneShapeAfter = kAddTileSceneShape | 0x80,
    kLookupTileCount = 2,
    kLookupTileMatchIndex = 1,
    kLookupTileMissIndex = -1,
    kLookupTileValue = 0x2345,
    kLookupTileShape = 0x67,
    kLookupTilePad = 0x89,
    kLookupOtherLod = 4,
    kLookupOtherSubIndex = 3,
    kLookupOtherX = 2,
    kLookupOtherY = 1,
    kLookupOtherValue = 0x1111,
    kLookupOtherShape = 0x44,
    kLookupOtherPad = 0x55,
    kVertexSignMaskEdgeCount = 2,
    kVertexNegativeNormal = -1,
    kVertexPositiveNormal = 1,
    kVertexFirstNormalOffset = 5,
    kVertexSecondNormalOffset = 13,
    kVertexFinalStreamOffset = 17,
    kVertexLowMaskAfterNegativeFirstEdge = -2,
    kVertexHighMaskUnchanged = -1,
    kVertexNarrowFlag = 0,
    kMapEventSurvivingType = 7,
    kMapEventExpiringType = 8,
    kMapEventSurvivingTtlBefore = 2,
    kMapEventSurvivingTtlAfter = 1,
    kMapEventExpiringTtlBefore = 1,
    kMapEventExpiringTtlAfter = 0,
    kMapEventClearedType = 0,
    kCountermeasureChaff = 2,
    kCountermeasureExhausted = 0,
    kWreckGravityStep = 12,
    kWreckStartAlt = 100,
    kWreckStartVel = 0,
    kWreckAfterFallAlt = kWreckStartAlt - kWreckGravityStep,
    kWreckAfterFallVel = -kWreckGravityStep,
    kWreckTerminalFallVelocity = -16,
    kWreckAfterTerminalAlt = kWreckStartAlt + kWreckTerminalFallVelocity,
    kWreckGroundAlt = 0,
    kWreckGroundVel = 7,
    kResetLocksGroundUnitCount = 3,
    kResetLocksInitialTrackedEnemy = 4,
    kResetLocksClearedTrackedEnemy = -1,
    kResetLocksSlot0Initial = 0,
    kResetLocksSlot1Initial = 1,
    kResetLocksSlot2Initial = 2,
    kResetLocksSlot3Untouched = 77,
    kResetLocksCleared = -1,
    kBulletTrackCountBaseline = 0,
    kBulletEvenFrameTick = 4,
    kBulletInitialPosX = 100,
    kBulletInitialPosY = 200,
    kBulletInitialAlt = 300,
    kBulletVelX = 5,
    kBulletVelY = -6,
    kBulletVelZ = 7,
    kBulletAfterPosX = kBulletInitialPosX + kBulletVelX,
    kBulletAfterPosY = kBulletInitialPosY + kBulletVelY,
    kBulletAfterAlt = kBulletInitialAlt + kBulletVelZ,
    kTracerSmokeSource = 3,
    kTracerNonSpawnFrameTick = 1,
    kTracerParticlePosX = 4,
    kTracerParticlePosY = 10,
    kTracerParticleAlt = 0x200,
    kTracerParticleAltRise = 10,
    kTracerParticleAltAfter = kTracerParticleAlt + kTracerParticleAltRise,
    kTracerParticlePosYAfter = kTracerParticlePosY + (kTracerParticleAltAfter >> 9),
    kTracerParticleSpin = 0,
    kTracerParticleSpinHighByteStep = 6,
    kTracerParticleSpinAfter = kTracerParticleSpinHighByteStep << 8,
    kAppendEventLimit = 255,
    kAppendMissionTick = 1234,
    kAppendViewX = 0x1234,
    kAppendViewY = 0x5678,
    kAppendScreenX = static_cast<unsigned>(kAppendViewX) >> 7,
    kAppendScreenY = static_cast<unsigned>(kAppendViewY) >> 7,
    kAppendEventType = 6,
    kAppendEventArg = 42,
    kAppendTerminatorType = 0,
    kAppendFullLogSentinelType = 77,
    kAppendFullLogIgnoredType = 1,
    kAppendFullLogIgnoredArg = 2,
    kDirectorFrameRateScaling = 20,
    kDirectorFrameTick = 100,
    kDirectorTimedKey = 0x77,
    kDirectorKeyValue = 0x89,
    kDirectorModeOff = 0,
    kDirectorModeOne = 1,
    kDirectorModeTwo = 2,
    kDirectorModeOneDelay = 3,
    kDirectorModeTwoDelay = 4,
    kDirectorModeOneDeadline = kDirectorFrameTick + kDirectorModeOneDelay * kDirectorFrameRateScaling,
    kDirectorModeTwoDeadline = kDirectorFrameTick + kDirectorModeTwoDelay * kDirectorFrameRateScaling,
    kDirectorNoDeadline = -1,
    kDirectorTargetModeTwo = 0x55,
    kDirectorTargetModeOne = 0x66,
    kDirectorTargetPendingRequest = 0x77,
    kDirectorRejectedPriority = 3,
    kDirectorAcceptedPriorityModeTwo = 2,
    kDirectorAcceptedPriorityModeOne = 1,
    kSlowMotionModeOne = 1,
    kSlowMotionModeTwo = 2,
    kRecalcFrameSyncDividend = 120,
    kRecalcFrameSyncBias = 9,
    kRecalcFrameSyncMin = 1,
    kRecalcFrameSyncMax = 4,
    kRecalcThreatTimerScale = 250,
    kRecalcThreatDisplayScale = 200,
    kRecalcHighScaleBefore = 20,
    kRecalcHighScaleAfter = 15,
    kRecalcHighScaleSlowMode = 0,
    kRecalcHighScaleFrameSync = 1,
    kRecalcHighScaleBulletTrackCount = 16,
    kRecalcHighScaleThreatTimer = kRecalcThreatTimerScale * kRecalcHighScaleAfter,
    kRecalcHighScaleThreatDisplay = kRecalcThreatDisplayScale * kRecalcHighScaleAfter,
    kRecalcSlowScaleBefore = 2,
    kRecalcSlowScaleAfter = 2,
    kRecalcSlowFrameSync = 0,
    kRecalcSlowBulletTrackCount = kRecalcSlowScaleAfter << 1,
    kRecalcSlowThreatTimer = kRecalcThreatTimerScale * kRecalcSlowScaleAfter,
    kRecalcSlowThreatDisplay = kRecalcThreatDisplayScale * kRecalcSlowScaleAfter,
    kSlowMotionScaleBefore = 6,
    kSlowMotionScaleAfter = kSlowMotionScaleBefore << 1,
    kSlowMotionInactiveScale = 9,
    kSlowMotionBulletTrackCount = 16,
    kSlowMotionThreatTimer = 250 * kSlowMotionScaleAfter,
    kSlowMotionThreatDisplay = 200 * kSlowMotionScaleAfter,
    kSelectMissileSlot = 2,
    kSelectMissileWeaponIndex = 5,
    kSelectMissileAmmo = 6,
    kSelectMissileHiddenHud = 0,
    kWeaponMarkerSelectedSlot = 1,
    kWeaponMarkerRequestedSlot = 2,
    kWeaponMarkerHiddenHud = 0,
};

constexpr const char *kReplaceExtensionOriginalPath = "KOREA.PLH";
constexpr const char *kReplaceExtensionNewSuffix = ".3dG";
constexpr const char *kReplaceExtensionExpectedPath = "KOREA.3dG";
constexpr const char *kCountermeasureExhaustedMessage = "Stores exhausted";
constexpr const char *kSelectMissileExpectedMessage = "Maverick armed";

constexpr std::array<int16, kAngleTableSize> makeOriginalAngleTable() {
    std::array<int16, kAngleTableSize> table{};
    for (std::size_t i = 0; i < table.size(); ++i) {
        table[i] = static_cast<int16>(static_cast<int>(i) * 97 - 12000);
    }
    return table;
}

constexpr auto kOriginalAngleTableValues = makeOriginalAngleTable();
int g_randStubValue = 0;

void require(bool condition, const char *message) {
    if (!condition) {
        std::cerr << "failed: " << message << '\n';
        std::exit(1);
    }
}

} // namespace

int16 g_mapCenterX = 0;
int16 g_mapCenterY = 0;
int16 g_mapZoomLevel = 8;
int16 g_hudVisible = 1;
int16 missileSpecIndex = 0;
int16 g_missionStatus = 0;
int16 g_scopeClipLeft = 0;
int16 g_scopeClipTop = 0;
int16 g_scopeClipRight = 0;
int16 g_scopeClipBottom = 0;
int16 g_mapMode = 0;
int16 g_lineX1 = 0;
int16 g_lineY1 = 0;
int16 g_lineX2 = 0;
int16 g_lineY2 = 0;
int16 g_drawPage = 0;
int16 g_viewportDescFront[11] = {};
int16 g_viewportDescMid[11] = {};
int16 *g_pageFront = g_viewportDescFront;
int16 *g_pageBack = g_viewportDescMid;
int16 g_frameRateScaling = kTacMapFrameRateScaling;
int16 g_timeAccelMode = 1;
int16 g_slowMotionMode = kSlowMotionModeOne;
int16 g_frameSyncWait = 0;
int16 frameTick = 0;
int16 g_bulletTrackCount = 0;
int16 g_threatTimerInit = 0;
int16 g_threatDisplayTtl = 0;
int16 g_setThrust = 0;
int16 g_inputDisabled = 0;
int16 g_axisInputAccum[4] = {};
int16 g_hudMsgTimer = 0;
int16 g_dirMsgTimer = 0;
int16 g_missionTick = 0;
char tempString[80] = {};
char string_3C04A[80] = {};
uint16 buf3d3[100] = {};
uint8 flt15_buf1[0x40] = {};
char far g_world3dData[AIRCRAFT_MODELS_OFFSET + 0x520C] = {};
uint8 quitFlag = 0;
char strBuf[78] = {};
char g_itoaScratch[12] = {};
int g_ourPitch = 0;
int16 g_ourRoll = 0;
int16 g_viewZ = 0;
int16 g_viewX_ = 0;
int16 g_viewY_ = 0;
int16 g_ourHead = 0;
int16 g_orientMatrix[9] = {};
int16 g_matrixScratch[9] = {};
int16 g_rotationCounter = 0;
char g_rollWasNonzero = 0;
char g_orientationDirty = 0;
int16 g_wreckAlt = 0;
int16 g_wreckFallVel = 0;
int16 g_viewPosX = 0;
int16 g_viewPosY = 0;
int16 g_viewPosZ = 0;
int16 g_viewCenterX = 0;
int16 g_viewCenterY = 0;
int16 g_tileWorldSize = 0;
int16 g_tileGridDim = 0;
int16 g_mapOriginX = 0;
int16 g_mapOriginY = 0;
int16 g_clipMaxX = 0;
int16 g_clipMaxY = 0;
int16 g_tileEntryIdx = 0;
int16 g_tileEntryCount = 0;
struct DynTileOverride g_dynTileEntries[94] = {};
struct NeighborSampling g_neighborSampling = {
    {-1, 1, 1, -1, 0, 1, 0, -1, 0},
    {1, 1, -1, -1, 1, 0, -1, 0, 0, -8192, -4096},
    {0, 0x1000, 0x2000}};
uint16 matrix3dt[5][32] = {};
struct TileSceneObject *matrix3dt_2[5][32] = {};
struct TileSceneObject *g_curTileEntry = nullptr;
struct TileObject nearestTile = {};
struct TileObject *g_nearestTileObj = nullptr;
int16 g_render3DTiles = 0;
int16 g_curLod = 0;
int16 g_planeCount = 0;
char far *g_modelStreamPtr = nullptr;
int16 g_modelEdgeCount = 0;
int16 g_modelWideVtxFlag = 0;
int16 g_vtxSignMaskLo = 0;
int16 g_vtxSignMaskHi = 0;
int16 g_camRotMatrix[9] = {};
int16 g_targetRange = 0;
int16 g_targetBearing = 0;
int16 g_acqRange = 0;
int16 g_acqAimY = 0;
struct GroundTargetTable g_planeTable = {};
struct Weapon aNone[23] = {
    {},
    {},
    {"SA-5", 350, 2, 0},
    {},
    {"SA-10", kThreatLethality, kThreatDangerTier, 1},
    {},
    {},
    {"SA-13", 125, 3, 0},
};
struct MissileSpec missleSpec[4] = {};
struct Missile missiles[20] = {
    {},
    {},
    {},
    {},
    {},
    {"AGM-65D", "Maverick", 0x1B, 6},
};
struct SimObject g_simObjects[20] = {};
struct Projectile g_projectiles[12] = {};
struct BulletTrack bulletTracks[20] = {};
struct Particle g_particles[8] = {};
struct MapEvent mapEvents[4] = {};
struct ReplayLog g_replayLog = {};
int16 g_eventLogCount = 0;
int16 g_eventTimers[3] = {};
int16 g_groundUnitCount = 0;
int16 g_targetEntityCount = 0;
int16 g_trackedEnemyIdx = -1;
int16 g_bombDamageMask = 0;
int16 g_playerPlaneFlags = 0;
int16 g_autopilotEngaged = 0;
int16 g_activePanelMode = 0;
int16 g_viewHeadingOffset = 0;
int16 g_gunAmmo = 0;
int16 g_gunFiredFlag = 0;
int16 g_gunHits = 0;
int16 g_damageTakenFlag = 0;
int16 g_ejectState = 0;
int16 g_smokeSourceIdx = -1;
int16 g_smokeParticleSlot = 0;
int16 g_directorEventDeadline = -1;
int g_directorMode = 0;
int16 keyValue = 0;
int16 g_viewTargetObj = 0;
extern const int16 g_weaponMarkerBoxX[3] = {76, 40, 115};
int16 g_weaponMarkerSel = 0;
struct GameComm far *commData = 0;
uint8 far *moveDst = 0;
uint8 g_waterTargetId[4] = {};
uint8 g_shapeTargetCategory[UNIT_STATE_COUNT] = {};
uint8 g_landTargetId[2] = {};
uint16 cursorX = 0;
uint16 cursorY = 0;
int16 worldBufOffset = 0;
int16 worldBufSegment = 0;
TargetBlock targetBlock = {};
struct WeaponDataBlock weaponDataBlock = {};
char gridFlags[256] = {};
uint8 flightDataBuf[0x600] = {};
char slotInfoTable[1194] = {};
char unitTypeTable[100] = {};
char ejectedFlag = 0;
int samKilled = 0;
int samMissed = 0;
int groundKilled = 0;
int groundMissed = 0;
int airKilled = 0;
int airMissed = 0;
int primaryHit = 0;
int secondaryHit = 0;
struct WorldObject worldObjects[0x4B] = {};
struct FlightUnit flightUnits[0x13] = {};
int missionResult = 0;
struct Game far *gameData = 0;
char bufCoordStr[5] = {};
char todayMissStrBuf[0x1D] = {};
uint8 missionStrTrunc = 0;
uint8 missionStrTruncEnd[1] = {};
char *wldOffsets[0x64] = {};
extern const int gridLevelSize[] = {0, 0x1000, 0x2000, 0x400, 0x100, 0x40, 0x10, 4};
uint8 gridBuf1[17] = {};
uint8 gridBuf2[0x100] = {};
uint8 gridBuf3[0x200] = {};
uint8 gridBuf4[0x200] = {};
uint8 gridBuf5[0x200] = {};
extern const struct Plane planes[19] = {
    {},
    {},
    {},
    {},
    {},
    {},
    {{}, {}, kPositionUnitMaxSpeed, kPositionUnitRange, {}},
};

extern "C" int rand() noexcept {
    return g_randStubValue;
}

int clampRange(int value, int minVal, int maxVal) { return original_clampRange(value, minVal, maxVal); }
int rangeApprox(int deltaX, int deltaY) { return original_rangeApprox(deltaX, deltaY); }
int computeBearing(int deltaX, int deltaY) { return original_computeBearing(deltaX, deltaY); }
int sinMul(int angle, int value) { return original_sinMul(angle, value); }
int cosMul(int angle, int value) { return original_cosMul(angle, value); }
int randomRange(int maxVal) { return original_randomRange(maxVal); }
int readAxisInput(int axisIdx) { return original_readAxisInput(axisIdx); }
void setDrawColor(int color) { original_setDrawColor(color); }
int drawCenteredLabelBox(int panel, const char *text) { return original_drawCenteredLabelBox(panel, text); }
int fillSpanRect(const int16 *, int, int, int, int) { return 0; }
int gfx_calcRowAddr(int, int) { return 0; }
void gfx_setBlitOffset(int) {}
void gfx_setColor(int) {}
void gfx_nop23(void) {}
int gfx_getDisplayPage(void) { return 0; }
void gfx_setPageN(uint16) {}
int drawClipLineGlobal(void) { return 0; }
int misc_readJoystick(int16) { return 0; }
void mystrcpy(char *dest, const char *source) { std::strcpy(dest, source); }
int mystrlen(const char *s) { return original_mystrlen(s); }
void mystrcat(char *dst, const char *src) { original_mystrcat(dst, src); }
void makeSound(int, int) {}
void tempStrcpy(const char *src) { original_tempStrcpy(src); }
void drawWeaponSelectMarker(int weaponIdx) { original_drawWeaponSelectMarker(weaponIdx); }
void setTimedMessage(char *) {}
uint32 scaleCoordToLod(int level, uint32 coord) { return original_scaleCoordToLod(level, coord); }
int process3dg(int, int, int) { return -1; }
void exitTimeAccel(void);
void original_exitSlowMotion(void) { exitTimeAccel(); }

void cleanup(void) {}
void restoreCbreakHandler(void) {}

std::string formatFlightTimeExpected(int timeValue, int miscBits, int target1Type, int target2Type) {
    int night = (miscBits & 0x03) == 0 ? 1 : 0;
    if (target1Type == kFormatFlightDayType || target2Type == kFormatFlightDayType) {
        night = 0;
    }
    if (target1Type == kFormatFlightNightType || target2Type == kFormatFlightNightType) {
        night = 1;
    }
    timeValue = static_cast<std::uint16_t>(timeValue + ((miscBits & 0x0F) << 8));
    char expected[9] = {};
    std::snprintf(expected, sizeof(expected), "%d%d:%02d:%02d",
                  night + 1,
                  (timeValue / 1800) % 10,
                  (timeValue / 30) % 60,
                  (timeValue * 2) % 60);
    return expected;
}

int loftAngleExpected(int pitch, int altitude) {
    const auto pitchMagnitude = static_cast<unsigned long>(std::abs(static_cast<int>(static_cast<int16>(pitch))));
    const auto numerator = static_cast<unsigned long>((0x4000UL - pitchMagnitude) << 12);
    const auto denominator = static_cast<unsigned int>(static_cast<uint16>(altitude + 0x1000));
    return static_cast<int>(numerator / denominator) - 0x4000;
}

/* Original eg3dmath.c/egmath.c/egflight.c read this exact global table. Keeping
 * it in this test makes the comparison use original code paths without pulling
 * in the whole egdata.c global block. */
extern const int16 g_angleLut[kAngleTableSize] = {
    kOriginalAngleTableValues[0],   kOriginalAngleTableValues[1],   kOriginalAngleTableValues[2],
    kOriginalAngleTableValues[3],   kOriginalAngleTableValues[4],   kOriginalAngleTableValues[5],
    kOriginalAngleTableValues[6],   kOriginalAngleTableValues[7],   kOriginalAngleTableValues[8],
    kOriginalAngleTableValues[9],   kOriginalAngleTableValues[10],  kOriginalAngleTableValues[11],
    kOriginalAngleTableValues[12],  kOriginalAngleTableValues[13],  kOriginalAngleTableValues[14],
    kOriginalAngleTableValues[15],  kOriginalAngleTableValues[16],  kOriginalAngleTableValues[17],
    kOriginalAngleTableValues[18],  kOriginalAngleTableValues[19],  kOriginalAngleTableValues[20],
    kOriginalAngleTableValues[21],  kOriginalAngleTableValues[22],  kOriginalAngleTableValues[23],
    kOriginalAngleTableValues[24],  kOriginalAngleTableValues[25],  kOriginalAngleTableValues[26],
    kOriginalAngleTableValues[27],  kOriginalAngleTableValues[28],  kOriginalAngleTableValues[29],
    kOriginalAngleTableValues[30],  kOriginalAngleTableValues[31],  kOriginalAngleTableValues[32],
    kOriginalAngleTableValues[33],  kOriginalAngleTableValues[34],  kOriginalAngleTableValues[35],
    kOriginalAngleTableValues[36],  kOriginalAngleTableValues[37],  kOriginalAngleTableValues[38],
    kOriginalAngleTableValues[39],  kOriginalAngleTableValues[40],  kOriginalAngleTableValues[41],
    kOriginalAngleTableValues[42],  kOriginalAngleTableValues[43],  kOriginalAngleTableValues[44],
    kOriginalAngleTableValues[45],  kOriginalAngleTableValues[46],  kOriginalAngleTableValues[47],
    kOriginalAngleTableValues[48],  kOriginalAngleTableValues[49],  kOriginalAngleTableValues[50],
    kOriginalAngleTableValues[51],  kOriginalAngleTableValues[52],  kOriginalAngleTableValues[53],
    kOriginalAngleTableValues[54],  kOriginalAngleTableValues[55],  kOriginalAngleTableValues[56],
    kOriginalAngleTableValues[57],  kOriginalAngleTableValues[58],  kOriginalAngleTableValues[59],
    kOriginalAngleTableValues[60],  kOriginalAngleTableValues[61],  kOriginalAngleTableValues[62],
    kOriginalAngleTableValues[63],  kOriginalAngleTableValues[64],  kOriginalAngleTableValues[65],
    kOriginalAngleTableValues[66],  kOriginalAngleTableValues[67],  kOriginalAngleTableValues[68],
    kOriginalAngleTableValues[69],  kOriginalAngleTableValues[70],  kOriginalAngleTableValues[71],
    kOriginalAngleTableValues[72],  kOriginalAngleTableValues[73],  kOriginalAngleTableValues[74],
    kOriginalAngleTableValues[75],  kOriginalAngleTableValues[76],  kOriginalAngleTableValues[77],
    kOriginalAngleTableValues[78],  kOriginalAngleTableValues[79],  kOriginalAngleTableValues[80],
    kOriginalAngleTableValues[81],  kOriginalAngleTableValues[82],  kOriginalAngleTableValues[83],
    kOriginalAngleTableValues[84],  kOriginalAngleTableValues[85],  kOriginalAngleTableValues[86],
    kOriginalAngleTableValues[87],  kOriginalAngleTableValues[88],  kOriginalAngleTableValues[89],
    kOriginalAngleTableValues[90],  kOriginalAngleTableValues[91],  kOriginalAngleTableValues[92],
    kOriginalAngleTableValues[93],  kOriginalAngleTableValues[94],  kOriginalAngleTableValues[95],
    kOriginalAngleTableValues[96],  kOriginalAngleTableValues[97],  kOriginalAngleTableValues[98],
    kOriginalAngleTableValues[99],  kOriginalAngleTableValues[100], kOriginalAngleTableValues[101],
    kOriginalAngleTableValues[102], kOriginalAngleTableValues[103], kOriginalAngleTableValues[104],
    kOriginalAngleTableValues[105], kOriginalAngleTableValues[106], kOriginalAngleTableValues[107],
    kOriginalAngleTableValues[108], kOriginalAngleTableValues[109], kOriginalAngleTableValues[110],
    kOriginalAngleTableValues[111], kOriginalAngleTableValues[112], kOriginalAngleTableValues[113],
    kOriginalAngleTableValues[114], kOriginalAngleTableValues[115], kOriginalAngleTableValues[116],
    kOriginalAngleTableValues[117], kOriginalAngleTableValues[118], kOriginalAngleTableValues[119],
    kOriginalAngleTableValues[120], kOriginalAngleTableValues[121], kOriginalAngleTableValues[122],
    kOriginalAngleTableValues[123], kOriginalAngleTableValues[124], kOriginalAngleTableValues[125],
    kOriginalAngleTableValues[126], kOriginalAngleTableValues[127], kOriginalAngleTableValues[128],
    kOriginalAngleTableValues[129], kOriginalAngleTableValues[130], kOriginalAngleTableValues[131],
    kOriginalAngleTableValues[132], kOriginalAngleTableValues[133], kOriginalAngleTableValues[134],
    kOriginalAngleTableValues[135], kOriginalAngleTableValues[136], kOriginalAngleTableValues[137],
    kOriginalAngleTableValues[138], kOriginalAngleTableValues[139], kOriginalAngleTableValues[140],
    kOriginalAngleTableValues[141], kOriginalAngleTableValues[142], kOriginalAngleTableValues[143],
    kOriginalAngleTableValues[144], kOriginalAngleTableValues[145], kOriginalAngleTableValues[146],
    kOriginalAngleTableValues[147], kOriginalAngleTableValues[148], kOriginalAngleTableValues[149],
    kOriginalAngleTableValues[150], kOriginalAngleTableValues[151], kOriginalAngleTableValues[152],
    kOriginalAngleTableValues[153], kOriginalAngleTableValues[154], kOriginalAngleTableValues[155],
    kOriginalAngleTableValues[156], kOriginalAngleTableValues[157], kOriginalAngleTableValues[158],
    kOriginalAngleTableValues[159], kOriginalAngleTableValues[160], kOriginalAngleTableValues[161],
    kOriginalAngleTableValues[162], kOriginalAngleTableValues[163], kOriginalAngleTableValues[164],
    kOriginalAngleTableValues[165], kOriginalAngleTableValues[166], kOriginalAngleTableValues[167],
    kOriginalAngleTableValues[168], kOriginalAngleTableValues[169], kOriginalAngleTableValues[170],
    kOriginalAngleTableValues[171], kOriginalAngleTableValues[172], kOriginalAngleTableValues[173],
    kOriginalAngleTableValues[174], kOriginalAngleTableValues[175], kOriginalAngleTableValues[176],
    kOriginalAngleTableValues[177], kOriginalAngleTableValues[178], kOriginalAngleTableValues[179],
    kOriginalAngleTableValues[180], kOriginalAngleTableValues[181], kOriginalAngleTableValues[182],
    kOriginalAngleTableValues[183], kOriginalAngleTableValues[184], kOriginalAngleTableValues[185],
    kOriginalAngleTableValues[186], kOriginalAngleTableValues[187], kOriginalAngleTableValues[188],
    kOriginalAngleTableValues[189], kOriginalAngleTableValues[190], kOriginalAngleTableValues[191],
    kOriginalAngleTableValues[192], kOriginalAngleTableValues[193], kOriginalAngleTableValues[194],
    kOriginalAngleTableValues[195], kOriginalAngleTableValues[196], kOriginalAngleTableValues[197],
    kOriginalAngleTableValues[198], kOriginalAngleTableValues[199], kOriginalAngleTableValues[200],
    kOriginalAngleTableValues[201], kOriginalAngleTableValues[202], kOriginalAngleTableValues[203],
    kOriginalAngleTableValues[204], kOriginalAngleTableValues[205], kOriginalAngleTableValues[206],
    kOriginalAngleTableValues[207], kOriginalAngleTableValues[208], kOriginalAngleTableValues[209],
    kOriginalAngleTableValues[210], kOriginalAngleTableValues[211], kOriginalAngleTableValues[212],
    kOriginalAngleTableValues[213], kOriginalAngleTableValues[214], kOriginalAngleTableValues[215],
    kOriginalAngleTableValues[216], kOriginalAngleTableValues[217], kOriginalAngleTableValues[218],
    kOriginalAngleTableValues[219], kOriginalAngleTableValues[220], kOriginalAngleTableValues[221],
    kOriginalAngleTableValues[222], kOriginalAngleTableValues[223], kOriginalAngleTableValues[224],
    kOriginalAngleTableValues[225], kOriginalAngleTableValues[226], kOriginalAngleTableValues[227],
    kOriginalAngleTableValues[228], kOriginalAngleTableValues[229], kOriginalAngleTableValues[230],
    kOriginalAngleTableValues[231], kOriginalAngleTableValues[232], kOriginalAngleTableValues[233],
    kOriginalAngleTableValues[234], kOriginalAngleTableValues[235], kOriginalAngleTableValues[236],
    kOriginalAngleTableValues[237], kOriginalAngleTableValues[238], kOriginalAngleTableValues[239],
    kOriginalAngleTableValues[240], kOriginalAngleTableValues[241], kOriginalAngleTableValues[242],
    kOriginalAngleTableValues[243], kOriginalAngleTableValues[244], kOriginalAngleTableValues[245],
    kOriginalAngleTableValues[246], kOriginalAngleTableValues[247], kOriginalAngleTableValues[248],
    kOriginalAngleTableValues[249], kOriginalAngleTableValues[250], kOriginalAngleTableValues[251],
    kOriginalAngleTableValues[252], kOriginalAngleTableValues[253], kOriginalAngleTableValues[254],
    kOriginalAngleTableValues[255], kOriginalAngleTableValues[256], kOriginalAngleTableValues[257],
    kOriginalAngleTableValues[258], kOriginalAngleTableValues[259],
};

int main() {
    const int sampleAngles[] = {
        kAngleNorth,
        1,
        kSineInterpolationRound - 1,
        kSineInterpolationRound,
        kAngleFractionMask,
        kWordDegreeStep,
        0x1234,
        kAngleQuarterTurn - 1,
        kAngleQuarterTurn,
        kAngleHalfTurn - 1,
        kAngleHalfTurn,
        kAngleThreeQuarterTurn - 1,
        kAngleThreeQuarterTurn,
        kAngleHalfTurn + kAngleFractionMask,
        kRawAngleMax,
    };
    for (int angle : sampleAngles) {
        require(original_sine(angle) == sine(Angle16(angle), g_angleLut).asInt(),
                "original sine matches fixed implementation");
        require(original_cosine(angle) == cosine(Angle16(angle), g_angleLut).asInt(),
                "original cosine matches fixed implementation");
        require(original_hudSine(angle) == sine(Angle16(angle), g_angleLut).asInt(),
                "original hudSine matches fixed implementation");
    }

    const int values[] = {
        kSignedWordMin,
        kSignedWordMinPlusOne,
        -20000,
        -16384,
        -1,
        0,
        1,
        12345,
        16384,
        20000,
        32766,
        kSignedWordMax,
    };
    for (int a : values) {
        for (int b : values) {
            require(original_fixedMulQ14(a, b) == Q15::multiplyToInt(a, b),
                    "original fixedMulQ14 matches fixed implementation");
        }
    }

    for (long value : {0L, 1L, -1L, 0x12345678L,
                       static_cast<long>(static_cast<std::int32_t>(0x80000000u)), 0x7fffffffL}) {
        for (int count : {0, 1, 3, 8, 15}) {
            long left = value;
            long right = value;
            original_shiftLongLeftInPlace(count, &left);
            original_shiftLongRightInPlace(count, &right);
            require(static_cast<std::int32_t>(left) == shiftLongLeft(static_cast<std::int32_t>(value), count),
                    "original shiftLongLeftInPlace matches fixed implementation");
            require(static_cast<std::int32_t>(right) == shiftLongRight(static_cast<std::int32_t>(value), count),
                    "original shiftLongRightInPlace matches fixed implementation");
        }
    }

    const int clampSamples[] = {
        kSignedWordMin,
        -20000,
        kClampWrapFloor,
        kClampWrapFloor + 1,
        -11,
        -10,
        -9,
        0,
        9,
        10,
        11,
        20000,
        kSignedWordMax,
    };
    for (int value : clampSamples) {
        require(original_clampValue(value, -10, 10) == clampValue(value, -10, 10),
                "original clampValue matches fixed implementation");
        require(original_clampRange(value, -10, 10) == f15::fixed::clampRange(value, -10, 10),
                "original clampRange matches fixed implementation");
        require(original_signOf(value) == signOf(value), "original signOf matches fixed implementation");
    }

    for (auto [dx, dy] : {std::pair<int, int>{0, 0}, std::pair<int, int>{10, 4},
                          std::pair<int, int>{-10, 4}, std::pair<int, int>{4, -10},
                          std::pair<int, int>{-4, -10}, std::pair<int, int>{40000, 40000},
                          std::pair<int, int>{kSignedWordMin, 0},
                          std::pair<int, int>{0, kSignedWordMin},
                          std::pair<int, int>{kSignedWordMax, kSignedWordMin}}) {
        require(original_rangeApprox(dx, dy) == f15::fixed::rangeApprox(dx, dy),
                "original rangeApprox matches fixed implementation");
        require(original_approxDistance(dx, dy) == f15::fixed::rangeApprox(dx, dy),
                "original start approxDistance matches fixed implementation");
    }

    worldObjects[kItemDistanceFirstIndex].x_coord = kItemDistanceFirstX;
    worldObjects[kItemDistanceFirstIndex].y_coord = kItemDistanceFirstY;
    worldObjects[kItemDistanceSecondIndex].x_coord = kItemDistanceSecondX;
    worldObjects[kItemDistanceSecondIndex].y_coord = kItemDistanceSecondY;
    require(original_itemDistance(kItemDistanceFirstIndex, kItemDistanceSecondIndex) ==
                f15::fixed::rangeApprox(kItemDistanceFirstX - kItemDistanceSecondX,
                                        kItemDistanceFirstY - kItemDistanceSecondY),
            "original itemDistance reads world-object coordinates and applies approxDistance");
    worldObjects[kPositionUnitLocationIndex].x_coord = kPositionUnitWorldX;
    worldObjects[kPositionUnitLocationIndex].y_coord = kPositionUnitWorldY;
    worldObjects[kPositionUnitLocationIndex].targetFlags = kPositionUnitLargeTargetFlag;
    flightUnits[kPositionUnitIndex].planeType = kPositionUnitPlaneType;
    flightUnits[kPositionUnitIndex].flags = kPositionUnitInitialFlags;
    original_positionUnit(kPositionUnitIndex, kPositionUnitLocationIndex);
    require(flightUnits[kPositionUnitIndex].waypointIdx == kPositionUnitLocationIndex &&
                flightUnits[kPositionUnitIndex].x == kPositionUnitX &&
                flightUnits[kPositionUnitIndex].y == kPositionUnitY &&
                flightUnits[kPositionUnitIndex].altitude == kPositionUnitAltitude &&
                flightUnits[kPositionUnitIndex].xPrecise == (kPositionUnitX << kPositionUnitWorldCoordShift) &&
                flightUnits[kPositionUnitIndex].yPrecise == (kPositionUnitY << kPositionUnitWorldCoordShift) &&
                flightUnits[kPositionUnitIndex].heading == static_cast<int16>(kPositionUnitHeading) &&
                flightUnits[kPositionUnitIndex].pitch == 0 &&
                flightUnits[kPositionUnitIndex].roll == 0 &&
                flightUnits[kPositionUnitIndex].flags == kPositionUnitFlags &&
                flightUnits[kPositionUnitIndex].maxSpeed == kPositionUnitMaxSpeed &&
                flightUnits[kPositionUnitIndex].fuel == kPositionUnitFuel,
            "original positionUnit places a flight unit at a world object using plane speed/range data");
    GameComm startComm = {};
    commData = &startComm;
    moveDst = nullptr;
    require(original_setMoveDstComm7A("ignored.wld", "wb") == kSetMoveDstSuccess &&
                moveDst == reinterpret_cast<uint8 *>(&startComm.worldBuf),
            "original setMoveDstComm7A points moveDst at commData->worldBuf and returns success");

    Game startGame = {};
    gameData = &startGame;
    startGame.theater = kFormatGridTheaterCC;
    require(original_formatGridRef(kFormatGridWorldX, kFormatGridWorldY, kFormatGridTheaterCC) == bufCoordStr &&
                std::strcmp(bufCoordStr, "CB87") == 0,
            "original formatGridRef applies theater prefix, offsets, and world-coordinate grid digits");
    std::memset(bufCoordStr, 0, sizeof(bufCoordStr));
    worldObjects[kFormatGridWorldObjectIndex].x_coord = kFormatGridWorldX;
    worldObjects[kFormatGridWorldObjectIndex].y_coord = kFormatGridWorldY;
    require(original_getItemCoordStr(kFormatGridWorldObjectIndex) == bufCoordStr &&
                std::strcmp(bufCoordStr, "CB87") == 0,
            "original getItemCoordStr formats coordinates from the selected world object");

    char depotLabel[] = "Depot";
    char baseLabel[] = "Base";
    std::memset(todayMissStrBuf, 0, sizeof(todayMissStrBuf));
    missionStrTrunc = kTargetLabelTruncSentinel;
    worldObjects[kTargetLabelWorldObjectIndex].unitRef = kTargetLabelUnitRef;
    worldObjects[kTargetLabelWorldObjectIndex].objectIdx = kTargetLabelObjectIndex;
    wldOffsets[kTargetLabelUnitRef] = depotLabel;
    wldOffsets[kTargetLabelObjectIndex] = baseLabel;
    original_buildTargetLabel(kTargetLabelWorldObjectIndex);
    require(std::strcmp(todayMissStrBuf, "Base at Depot") == 0 &&
                missionStrTrunc == kTargetLabelTruncSentinel,
            "original buildTargetLabel joins object and unit labels without truncating short text");

    for (auto [dx, dy] : {std::pair<int, int>{0, 1}, std::pair<int, int>{0, -1},
                          std::pair<int, int>{1, 0}, std::pair<int, int>{-1, 0},
                          std::pair<int, int>{100, 100}, std::pair<int, int>{100, -50},
                          std::pair<int, int>{-50, 100}, std::pair<int, int>{-100, -20},
                          std::pair<int, int>{7, -123}, std::pair<int, int>{123, 7},
                          std::pair<int, int>{-123, 7}, std::pair<int, int>{7, 123},
                          std::pair<int, int>{-7, -123},
                          std::pair<int, int>{kSignedWordMax, 1},
                          std::pair<int, int>{1, kSignedWordMax}}) {
        require(static_cast<std::uint16_t>(original_computeBearing(dx, dy)) == f15::fixed::computeBearing(dx, dy).raw(),
                "original computeBearing matches fixed implementation");
        require(static_cast<std::uint16_t>(original_calcBearing(dx, dy)) == f15::fixed::computeBearing(dx, dy).raw(),
                "original start calcBearing matches fixed implementation");
    }
    for (auto [angle, scalar] : {std::pair<int, int>{0, 1000}, std::pair<int, int>{0x1234, -2000},
                                 std::pair<int, int>{kAngleQuarterTurn, 32767},
                                 std::pair<int, int>{kAngleHalfTurn, kSignedWordMin},
                                 std::pair<int, int>{kRawAngleMax, 1},
                                 std::pair<int, int>{0x80FF, 16384}}) {
        require(original_sinMul(angle, scalar) == sinMul(Angle16(angle), scalar, g_angleLut),
                "original sinMul matches fixed implementation");
        require(original_cosMul(angle, scalar) == cosMul(Angle16(angle), scalar, g_angleLut),
                "original cosMul matches fixed implementation");
    }

    for (auto [num, den] : {std::pair{0, 1}, std::pair{1, 1}, std::pair{-1, 1},
                            std::pair{1, -1}, std::pair{-1, -1}, std::pair{16383, 32767},
                            std::pair{-16383, 32767}, std::pair{32767, 32767},
                            std::pair{-32767, 32767}, std::pair{-12000, -24000},
                            std::pair{12345, 23456}}) {
        require(static_cast<std::uint16_t>(original_signedRatio16(num, den)) == signedRatio16Bits(num, den),
                "original signedRatio16 matches fixed implementation");
    }
    const int inverseTrigSamples[] = {
        kSignedWordMin,
        kSignedWordMinPlusOne,
        -4096,
        -2048,
        -513,
        -512,
        -1,
        0,
        1,
        511,
        512,
        2048,
        4096,
        32766,
        kSignedWordMax,
    };
    for (int value : inverseTrigSamples) {
        require(static_cast<std::uint16_t>(original_valueToAngle(value)) == valueToAngle(value, g_angleLut).raw(),
                "original valueToAngle matches fixed implementation");
        require(static_cast<std::uint16_t>(original_complementAngle(value)) == complementAngle(value, g_angleLut).raw(),
                "original complementAngle matches fixed implementation");
    }
    const int sqrtSamples[] = {kSignedWordMin, kSignedWordMinPlusOne, -10000, -1024, -17, -4, -3, -1,
                               0, 1, 3, 4, 15, 16, 17, 255, 1024, 4096, 16384, kSignedWordMax};
    for (int value : sqrtSamples) {
        require(original_isqrt(value) == integerSqrtCompatible(value),
                "original isqrt matches fixed implementation");
    }
    const int pitchSamples[] = {0, 1, -1, kAngleQuarterTurn, kAngleHalfTurn, kRawAngleMax};
    for (int pitch : pitchSamples) {
        require(original_hudPitchScale(static_cast<std::uint16_t>(pitch)) == hudPitchScale(pitch),
                "original hudPitchScale matches fixed implementation");
    }

    const int aspectSamples[] = {kSignedWordMin, -200, -1, 0, 1, 40, 199, 320, kSignedWordMax};
    for (int screenY : aspectSamples) {
        require(original_aspectScaleY(screenY) == screenY - (screenY >> kAspectScaleShift),
                "original aspectScaleY matches 3/4 vertical scale");
    }

    for (auto [centerX, centerY, zoom, mapX, mapY] : {
             std::tuple<int, int, int, int, int>{0, 0, 8, 100, 100},
             std::tuple<int, int, int, int, int>{0x2000, 0x3000, 8, 0x2400, 0x3400},
             std::tuple<int, int, int, int, int>{-100, 200, 6, -400, 800},
         }) {
        g_mapCenterX = static_cast<int16>(centerX);
        g_mapCenterY = static_cast<int16>(centerY);
        g_mapZoomLevel = static_cast<int16>(zoom);
        const int shift = 10 - zoom;
        require(original_mapXToScreen(mapX) == (((mapX - centerX) >> shift) + 60),
                "original mapXToScreen matches tactical-map center/zoom formula");
        require(original_mapYToScreen(mapY) == (((((mapY - centerY) >> shift) * 3) >> 2) + 140),
                "original mapYToScreen matches tactical-map center/zoom formula");
    }

    g_hudVisible = 1;
    g_mapCenterX = kObjectMapCenterX;
    g_mapCenterY = kObjectMapCenterY;
    g_mapZoomLevel = 8;
    g_scopeClipLeft = 0;
    g_scopeClipTop = 0;
    g_scopeClipRight = kObjectClipRight;
    g_scopeClipBottom = kObjectClipBottom;
    int16 objectScreenX = 0;
    int16 objectScreenY = 0;
    require(original_objectToScreen(kObjectMapCenterX, kObjectMapCenterY, &objectScreenX, &objectScreenY) == 1 &&
                objectScreenX == kObjectScreenCenterX && objectScreenY == kObjectScreenCenterY,
            "original objectToScreen writes tactical-map center coordinates inside clip");
    require(original_plotMapObject(kObjectMapCenterX, kObjectMapCenterY, kPlotMapObjectHiddenColor,
                                   kPlotMapObjectSmallMarker) == kPlotMapObjectHiddenResult,
            "original plotMapObject reports hidden color as clipped/hidden without drawing");

    original_setViewPosition(kViewPositionX, kViewPositionY, kViewPositionZ);
    require(g_viewPosX == kViewPositionX && g_viewPosY == kViewPositionY && g_viewPosZ == kViewPositionZ,
            "original setViewPosition stores camera position globals");

    int16 identityA[9] = {};
    int16 identityB[9] = {};
    identityA[0] = identityA[4] = identityA[8] = kAttitudeIdentityDiagonal;
    identityB[0] = identityB[4] = identityB[8] = kAttitudeIdentityDiagonal;
    g_rotationCounter = kRotationDirtyCounterBefore;
    g_orientationDirty = 0;
    original_applyRotationDelta(identityA, identityB);
    require(g_rotationCounter == kRotationDirtyCounterAfter &&
                g_orientationDirty == kOrientationDirty &&
                g_orientMatrix[0] == kAttitudeProductDiagonal &&
                g_orientMatrix[4] == kAttitudeProductDiagonal &&
                g_orientMatrix[8] == kAttitudeProductDiagonal,
            "original applyRotationDelta multiplies identity matrices and dirties every eighth rotation");

    std::memset(g_orientMatrix, 0, sizeof(g_orientMatrix));
    g_orientMatrix[0] = kAttitudeIdentityDiagonal;
    g_orientMatrix[4] = kAttitudeIdentityDiagonal;
    g_orientMatrix[8] = kAttitudeIdentityDiagonal;
    g_rollWasNonzero = 0;
    g_orientationDirty = 0;
    original_computeAttitudeAngles();
    const int configuredZeroAngle = original_valueToAngle(kAttitudeValueToAngleZeroInput);
    require(g_ourHead == configuredZeroAngle &&
                g_ourPitch == configuredZeroAngle &&
                g_ourRoll == configuredZeroAngle &&
                g_orientationDirty == 0,
            "original computeAttitudeAngles derives identity attitude from the configured angle table");

    g_hudVisible = kThrottleHiddenHud;
    original_UpdateThrottleState();
    require(g_hudVisible == kThrottleHiddenHud,
            "original UpdateThrottleState preserves hidden-HUD no-op state");

    g_viewCenterX = kWorldTileViewCenterX;
    g_viewCenterY = kWorldTileViewCenterY;
    g_mapOriginX = kWorldTileMapOriginX;
    g_mapOriginY = kWorldTileMapOriginY;
    g_tileWorldSize = kWorldTileSize;
    int tileCol = 0;
    int tileRow = 0;
    original_worldToTileIndex(kWorldTileWorldX, kWorldTileWorldY, &tileCol, &tileRow);
    require(tileCol == kWorldTileOutCol && tileRow == kWorldTileOutRow,
            "original worldToTileIndex preserves centered 4:3 tile conversion");

    g_viewCenterX = kTileBoundsViewCenterX;
    g_viewCenterY = kTileBoundsViewCenterY;
    g_mapOriginX = kTileBoundsMapOriginX;
    g_mapOriginY = kTileBoundsMapOriginY;
    g_tileWorldSize = kTileBoundsTileWorldSize;
    g_tileGridDim = kTileBoundsGridDim;
    g_clipMaxX = kTileBoundsClipMaxX;
    g_clipMaxY = kTileBoundsClipMaxY;
    int minTileX = -1;
    int maxTileX = -1;
    int minTileY = -1;
    int maxTileY = -1;
    original_computeTileBounds(&minTileX, &maxTileX, &minTileY, &maxTileY);
    require(minTileX == kTileBoundsMinX && maxTileX == kTileBoundsMaxX &&
                minTileY == kTileBoundsMinY && maxTileY == kTileBoundsMaxY,
            "original computeTileBounds clamps visible tile span to map grid");

    std::memset(g_dynTileEntries, 0, sizeof(g_dynTileEntries));
    g_tileEntryCount = kAddTileInitialCount;
    TileSceneObject tileScene = {};
    tileScene.shape = kAddTileSceneShape;
    TileObject tileObject = {};
    tileObject.entry = &tileScene;
    tileObject.lod = kAddTileLod;
    tileObject.subIndex = kAddTileSubIndex;
    tileObject.tileX = kAddTileX;
    tileObject.tileY = kAddTileY;
    tileObject.pad15 = kAddTilePad;
    original_addTileEntry(&tileObject, kAddTileShapeOff, kAddTileFlag);
    const DynTileOverride &tileOverride = g_dynTileEntries[kAddTileInitialCount];
    require(g_tileEntryCount == kAddTileInitialCount + 1 &&
                tileObject.shapeOff == kAddTileShapeOff &&
                tileObject.flag == kAddTileFlag &&
                tileObject.pad15 == kAddTilePad &&
                tileScene.shape == kAddTileSceneShapeAfter &&
                tileOverride.lod == kAddTileLod &&
                tileOverride.subIndex == kAddTileSubIndex &&
                tileOverride.tileX == kAddTileX &&
                tileOverride.tileY == kAddTileY &&
                tileOverride.value == kAddTileShapeOff &&
                tileOverride.shape == kAddTileFlag &&
                tileOverride.pad7 == kAddTilePad,
            "original addTileEntry appends a dynamic tile override and marks the source shape dynamic");

    std::memset(g_dynTileEntries, 0, sizeof(g_dynTileEntries));
    g_tileEntryCount = kLookupTileCount;
    g_dynTileEntries[0].lod = kLookupOtherLod;
    g_dynTileEntries[0].subIndex = kLookupOtherSubIndex;
    g_dynTileEntries[0].tileX = kLookupOtherX;
    g_dynTileEntries[0].tileY = kLookupOtherY;
    g_dynTileEntries[0].value = kLookupOtherValue;
    g_dynTileEntries[0].shape = kLookupOtherShape;
    g_dynTileEntries[0].pad7 = kLookupOtherPad;
    g_dynTileEntries[1].lod = kAddTileLod;
    g_dynTileEntries[1].subIndex = kAddTileSubIndex;
    g_dynTileEntries[1].tileX = kAddTileX;
    g_dynTileEntries[1].tileY = kAddTileY;
    g_dynTileEntries[1].value = kLookupTileValue;
    g_dynTileEntries[1].shape = kLookupTileShape;
    g_dynTileEntries[1].pad7 = kLookupTilePad;
    require(original_lookupTileEntry(kAddTileLod, kAddTileSubIndex, kAddTileX, kAddTileY) == kLookupTileValue &&
                g_tileEntryIdx == kLookupTileMatchIndex,
            "original lookupTileEntry scans dynamic overrides from the newest entry and returns the matched value");
    require(original_lookupTileEntry(kLookupOtherLod, kAddTileSubIndex, kAddTileX, kAddTileY) == 0 &&
                g_tileEntryIdx == kLookupTileMissIndex,
            "original lookupTileEntry returns zero and leaves index at -1 when no override matches");

    uint8 vertexStream[20] = {};
    vertexStream[0] = kVertexSignMaskEdgeCount;
    *reinterpret_cast<int16 *>(vertexStream + kVertexFirstNormalOffset) = kVertexNegativeNormal;
    *reinterpret_cast<int16 *>(vertexStream + kVertexSecondNormalOffset) = kVertexPositiveNormal;
    g_modelStreamPtr = reinterpret_cast<char *>(vertexStream);
    original_buildVertexSignMask(0, 0);
    require(g_modelStreamPtr == reinterpret_cast<char *>(vertexStream + kVertexFinalStreamOffset) &&
                g_modelEdgeCount == kVertexSignMaskEdgeCount &&
                g_modelWideVtxFlag == kVertexNarrowFlag &&
                g_vtxSignMaskLo == kVertexLowMaskAfterNegativeFirstEdge &&
                g_vtxSignMaskHi == kVertexHighMaskUnchanged,
            "original buildVertexSignMask advances the model stream and flips mask bits for negative edge normals");

    std::memset(mapEvents, 0, sizeof(mapEvents));
    mapEvents[0].type = kMapEventSurvivingType;
    mapEvents[0].ttl = kMapEventSurvivingTtlBefore;
    mapEvents[1].type = kMapEventExpiringType;
    mapEvents[1].ttl = kMapEventExpiringTtlBefore;
    original_tickMessageTimers();
    require(mapEvents[0].type == kMapEventSurvivingType &&
                mapEvents[0].ttl == kMapEventSurvivingTtlAfter &&
                mapEvents[1].type == kMapEventClearedType &&
                mapEvents[1].ttl == kMapEventExpiringTtlAfter,
            "original tickMessageTimers decrements live map-event timers and clears expired type");

    g_wreckAlt = kWreckStartAlt;
    g_wreckFallVel = kWreckStartVel;
    original_applyGravityFall();
    require(g_wreckFallVel == kWreckAfterFallVel && g_wreckAlt == kWreckAfterFallAlt,
            "original applyGravityFall applies gravity while wreck is above ground");
    g_wreckAlt = kWreckStartAlt;
    g_wreckFallVel = kWreckTerminalFallVelocity;
    original_applyGravityFall();
    require(g_wreckFallVel == kWreckTerminalFallVelocity && g_wreckAlt == kWreckAfterTerminalAlt,
            "original applyGravityFall preserves terminal fall velocity clamp");
    g_wreckAlt = kWreckGroundAlt;
    g_wreckFallVel = kWreckGroundVel;
    original_applyGravityFall();
    require(g_wreckAlt == kWreckGroundAlt && g_wreckFallVel == kWreckGroundVel,
            "original applyGravityFall ignores wrecks at ground level");

    g_groundUnitCount = kResetLocksGroundUnitCount;
    g_trackedEnemyIdx = kResetLocksInitialTrackedEnemy;
    g_simObjects[0].terrainColor = kResetLocksSlot0Initial;
    g_simObjects[1].terrainColor = kResetLocksSlot1Initial;
    g_simObjects[2].terrainColor = kResetLocksSlot2Initial;
    g_simObjects[3].terrainColor = kResetLocksSlot3Untouched;
    original_resetSimObjectLocks();
    require(g_simObjects[0].terrainColor == kResetLocksCleared &&
                g_simObjects[1].terrainColor == kResetLocksCleared &&
                g_simObjects[2].terrainColor == kResetLocksCleared &&
                g_simObjects[3].terrainColor == kResetLocksSlot3Untouched &&
                g_trackedEnemyIdx == kResetLocksClearedTrackedEnemy,
            "original resetSimObjectLocks clears terrain locks up to ground-unit count and resets tracked enemy");

    std::memset(bulletTracks, 0, sizeof(bulletTracks));
    g_bulletTrackCount = kBulletTrackCountBaseline;
    frameTick = kBulletEvenFrameTick;
    bulletTracks[0].posX = kBulletInitialPosX;
    bulletTracks[0].posY = kBulletInitialPosY;
    bulletTracks[0].alt = kBulletInitialAlt;
    bulletTracks[0].velX = kBulletVelX;
    bulletTracks[0].velY = kBulletVelY;
    bulletTracks[0].velZ = kBulletVelZ;
    original_updateBulletsAndFire();
    require(bulletTracks[0].posX == kBulletAfterPosX &&
                bulletTracks[0].posY == kBulletAfterPosY &&
                bulletTracks[0].alt == kBulletAfterAlt &&
                bulletTracks[1].posX == 0,
            "original updateBulletsAndFire advances existing bullet tracks on even frames without firing");

    std::memset(g_particles, 0, sizeof(g_particles));
    g_smokeSourceIdx = kTracerSmokeSource;
    frameTick = kTracerNonSpawnFrameTick;
    g_particles[0].posX = kTracerParticlePosX;
    g_particles[0].posY = kTracerParticlePosY;
    g_particles[0].alt = kTracerParticleAlt;
    g_particles[0].spin = kTracerParticleSpin;
    original_updateTracerParticles();
    require(g_particles[0].posX == kTracerParticlePosX &&
                g_particles[0].posY == kTracerParticlePosYAfter &&
                g_particles[0].alt == kTracerParticleAltAfter &&
                g_particles[0].spin == kTracerParticleSpinAfter,
            "original updateTracerParticles rises smoke particles and advances spin on non-spawn frames");

    g_frameRateScaling = kRecalcHighScaleBefore;
    g_timeAccelMode = kRecalcHighScaleSlowMode;
    g_frameSyncWait = 0;
    original_recalcTimeScale();
    require(g_frameSyncWait == kRecalcHighScaleFrameSync &&
                g_frameRateScaling == kRecalcHighScaleAfter &&
                g_bulletTrackCount == kRecalcHighScaleBulletTrackCount &&
                g_threatTimerInit == kRecalcHighScaleThreatTimer &&
                g_threatDisplayTtl == kRecalcHighScaleThreatDisplay,
            "original recalcTimeScale computes frame sync before clamping high frame-rate scale");
    g_frameRateScaling = kRecalcSlowScaleBefore;
    g_timeAccelMode = kSlowMotionModeTwo;
    g_frameSyncWait = 0x1234;
    original_recalcTimeScale();
    require(g_frameSyncWait == kRecalcSlowFrameSync &&
                g_frameRateScaling == kRecalcSlowScaleAfter &&
                g_bulletTrackCount == kRecalcSlowBulletTrackCount &&
                g_threatTimerInit == kRecalcSlowThreatTimer &&
                g_threatDisplayTtl == kRecalcSlowThreatDisplay,
            "original recalcTimeScale preserves mode-2 slow-motion minimum scale");

    g_timeAccelMode = kSlowMotionModeTwo;
    g_frameRateScaling = kSlowMotionScaleBefore;
    original_exitSlowMotion();
    require(g_timeAccelMode == kSlowMotionModeOne &&
                g_frameRateScaling == kSlowMotionScaleAfter &&
                g_bulletTrackCount == kSlowMotionBulletTrackCount &&
                g_threatTimerInit == kSlowMotionThreatTimer &&
                g_threatDisplayTtl == kSlowMotionThreatDisplay,
            "original exitSlowMotion exits mode 2 and recalculates frame-rate dependent timers");
    g_timeAccelMode = kSlowMotionModeOne;
    g_frameRateScaling = kSlowMotionInactiveScale;
    original_exitSlowMotion();
    require(g_timeAccelMode == kSlowMotionModeOne &&
                g_frameRateScaling == kSlowMotionInactiveScale,
            "original exitSlowMotion ignores calls when already out of mode 2");

    std::memset(&g_replayLog, 0, sizeof(g_replayLog));
    g_eventLogCount = 0;
    g_missionTick = kAppendMissionTick;
    g_viewX_ = kAppendViewX;
    g_viewY_ = kAppendViewY;
    g_replayLog.events[1].type = kAppendFullLogSentinelType;
    g_replayLog.events[1].arg = kAppendFullLogSentinelType;
    original_appendMapEvent(kAppendEventType, kAppendEventArg);
    require(g_eventLogCount == 1 &&
                g_replayLog.events[0].coord == kAppendMissionTick &&
                g_replayLog.events[0].screenX == kAppendScreenX &&
                g_replayLog.events[0].screenY == kAppendScreenY &&
                g_replayLog.events[0].type == kAppendEventType &&
                g_replayLog.events[0].arg == kAppendEventArg &&
                g_replayLog.events[1].type == kAppendTerminatorType &&
                g_replayLog.events[1].arg == kAppendFullLogSentinelType,
            "original appendMapEvent stores event data and writes the following terminator type");

    g_eventLogCount = kAppendEventLimit;
    g_replayLog.events[kAppendEventLimit].type = kAppendFullLogSentinelType;
    original_appendMapEvent(kAppendFullLogIgnoredType, kAppendFullLogIgnoredArg);
    require(g_eventLogCount == kAppendEventLimit &&
                g_replayLog.events[kAppendEventLimit].type == kAppendFullLogSentinelType,
            "original appendMapEvent ignores events once the replay log is full");

    g_frameRateScaling = kDirectorFrameRateScaling;
    frameTick = kDirectorFrameTick;
    g_directorMode = kDirectorModeOff;
    keyValue = 0;
    g_directorEventDeadline = kDirectorNoDeadline;
    g_viewTargetObj = 0;
    original_scheduleTimedEvent(kDirectorTimedKey, kDirectorModeTwoDelay);
    require(keyValue == 0 && g_directorEventDeadline == kDirectorNoDeadline && g_viewTargetObj == 0,
            "original scheduleTimedEvent ignores requests when director mode is off");

    g_directorMode = kDirectorModeTwo;
    original_scheduleTimedEvent(kDirectorTimedKey, kDirectorModeTwoDelay);
    require(keyValue == kDirectorTimedKey && g_directorEventDeadline == kDirectorModeTwoDeadline,
            "original scheduleTimedEvent stores key and scaled deadline");

    keyValue = 0;
    g_directorEventDeadline = kDirectorNoDeadline;
    g_viewTargetObj = 0;
    original_scheduleEventCheck(kDirectorTargetModeTwo, kDirectorRejectedPriority);
    require(keyValue == 0 && g_directorEventDeadline == kDirectorNoDeadline && g_viewTargetObj == 0,
            "original scheduleEventCheck rejects priorities above director mode");

    original_scheduleEventCheck(kDirectorTargetModeTwo, kDirectorAcceptedPriorityModeTwo);
    require(g_viewTargetObj == kDirectorTargetModeTwo && keyValue == kDirectorKeyValue &&
                g_directorEventDeadline == kDirectorModeTwoDeadline,
            "original scheduleEventCheck schedules mode-2 director event");

    g_directorMode = kDirectorModeOne;
    g_directorEventDeadline = kDirectorNoDeadline;
    keyValue = 0;
    g_viewTargetObj = 0;
    original_scheduleEventCheck(kDirectorTargetModeOne, kDirectorAcceptedPriorityModeOne);
    require(g_viewTargetObj == kDirectorTargetModeOne && keyValue == kDirectorKeyValue &&
                g_directorEventDeadline == kDirectorModeOneDeadline,
            "original scheduleEventCheck schedules mode-1 director event");

    original_scheduleEventCheck(kDirectorTargetPendingRequest, kDirectorAcceptedPriorityModeOne);
    require(g_viewTargetObj == kDirectorTargetModeOne && g_directorEventDeadline == kDirectorModeOneDeadline,
            "original scheduleEventCheck ignores requests while an event is pending");

    g_frameRateScaling = kTacMapFrameRateScaling;
    original_setDrawColor(kTacMapDrawColor);
    require(g_pageFront[2] == kTacMapDrawColor && g_pageBack[2] == kTacMapDrawColor,
            "original setDrawColor updates front and back page descriptors");
    original_tempStrcpy("status");
    require(std::strcmp(tempString, "status") == 0 && g_hudMsgTimer == kTacMapThreeSecondTimer,
            "original tempStrcpy copies HUD text and sets the three-second timer");
    g_eventTimers[kCountermeasureChaff] = kCountermeasureExhausted;
    std::memset(tempString, 0, sizeof(tempString));
    original_countermeasures(kCountermeasureChaff);
    require(g_eventTimers[kCountermeasureChaff] == kCountermeasureExhausted &&
                std::strcmp(tempString, kCountermeasureExhaustedMessage) == 0,
            "original countermeasures clamps exhausted stores and reports warning");
    missileSpecIndex = kSelectMissileSlot;
    missleSpec[kSelectMissileSlot].weaponIdx = kSelectMissileWeaponIndex;
    missleSpec[kSelectMissileSlot].ammo = kSelectMissileAmmo;
    g_hudVisible = kSelectMissileHiddenHud;
    std::memset(tempString, 0, sizeof(tempString));
    original_selectMissile();
    require(std::strcmp(tempString, kSelectMissileExpectedMessage) == 0,
            "original selectMissile reports the selected armed weapon");
    g_hudVisible = 1;
    g_hudVisible = kWeaponMarkerHiddenHud;
    g_weaponMarkerSel = kWeaponMarkerSelectedSlot;
    original_drawWeaponSelectMarker(kWeaponMarkerRequestedSlot);
    require(g_hudVisible == kWeaponMarkerHiddenHud && g_weaponMarkerSel == kWeaponMarkerSelectedSlot,
            "original drawWeaponSelectMarker is a no-op while the HUD is hidden");
    g_hudVisible = 1;
    char directorMessage[] = "director";
    original_setTimedMessage(directorMessage);
    require(std::strcmp(string_3C04A, "director") == 0 && g_dirMsgTimer == kTacMapThreeSecondTimer,
            "original setTimedMessage copies director text and sets the three-second timer");

    for (auto [level, coord] : {
             std::pair<int, std::uint32_t>{0, 0},
             std::pair<int, std::uint32_t>{0, 1000},
             std::pair<int, std::uint32_t>{1, 1000},
             std::pair<int, std::uint32_t>{2, 0x1234},
             std::pair<int, std::uint32_t>{3, 0x1234},
             std::pair<int, std::uint32_t>{4, 0x1234},
         }) {
        std::uint32_t rounded = 0;
        std::uint32_t truncated = 0;
        switch (level) {
        case 4:
            rounded = (coord + 0x20) >> 6;
            truncated = coord >> 6;
            break;
        case 3:
            rounded = (coord + 8) >> 4;
            truncated = coord >> 4;
            break;
        case 2:
            rounded = (coord + 2) >> 2;
            truncated = coord >> 2;
            break;
        case 1:
            rounded = truncated = coord;
            break;
        default:
            rounded = truncated = coord << 1;
            break;
        }
        require(original_scaleCoordToLod(level, coord) == rounded,
                "original scaleCoordToLod matches rounded renderer LOD scaling");
        require(original_scaleCoordByLevel(level, coord) == truncated,
                "original scaleCoordByLevel matches terrain LOD scaling");
    }
    gridBuf1[kLookupGridDirectCol + (kLookupGridDirectRow << 2)] = kLookupGridDirectValue;
    require(original_lookupGridCell(kLookupGridLevel4, kLookupGridDirectCol, kLookupGridDirectRow) ==
                kLookupGridDirectValue,
            "original lookupGridCell reads direct level-4 grid cells");
    gridBuf2[kLookupGridParentIndex] = kLookupGridParentCell;
    gridBuf3[kLookupGridNestedIndex] = kLookupGridNestedValue;
    require(original_lookupGridCell(kLookupGridLevel2, kLookupGridNestedCol, kLookupGridNestedRow) ==
                kLookupGridNestedValue,
            "original lookupGridCell resolves parent cells for nested level-2 grid lookups");
    require(original_lookupGridCell(kLookupGridLevel4, kLookupGridOutOfRangeCol, kLookupGridDirectRow) ==
                kLookupGridNotFound,
            "original lookupGridCell rejects coordinates outside the level bounds");

    buf3d3[0] = 0;
    buf3d3[kShapeOffsetTableSlot] = kDynamicShapeSlotOffset;
    reinterpret_cast<int16 *>(flt15_buf1)[0] = 0;
    reinterpret_cast<int16 *>(flt15_buf1)[1] = kAircraftModelSlotOffset;
    require(original_shapeDataOffset(0) == AIRCRAFT_MODELS_OFFSET,
            "original shapeDataOffset maps zero aircraft model slot to aircraft base");
    require(original_shapeDataOffset(1) == AIRCRAFT_MODELS_OFFSET + kAircraftModelSlotOffset,
            "original shapeDataOffset adds aircraft model table offsets");
    require(original_shapeDataOffset(kDynamicShapeFlag) == 0,
            "original shapeDataOffset maps dynamic shape zero through buf3d3");
    require(original_shapeDataOffset(kDynamicShapeFlag | kShapeOffsetTableSlot) == kDynamicShapeSlotOffset,
            "original shapeDataOffset maps dynamic shape ids through buf3d3");

    int noopSentinel = kSignedWordMax;
    original_doNothing3();
    original_doNothing4();
    original_doNothing(nullptr);
    require(original_drawCenteredLabelBox(2, "READY") == 0,
            "original drawCenteredLabelBox preserves the no-op label-box return value");
    require(noopSentinel == kSignedWordMax, "original doNothing entry points return without side effects");
    quitFlag = 0;
    original_checkQuitFlag();
    require(quitFlag == 0, "original checkQuitFlag returns without side effects when quit flag is clear");
    original_installCBreakHandler();
    original_restoreCbreakHandler();
    require(noopSentinel == kSignedWordMax, "original CBreak handler stubs return without side effects");
    require(original_mystrlen("F15.spr") == static_cast<int>(std::strlen("F15.spr")),
            "original mystrlen returns the original byte count");
    char copyText[kMyStrcpyBufferBytes] = {};
    original_mystrcpy(copyText, "Hello");
    require(std::strcmp(copyText, "Hello") == 0, "original mystrcpy copies source text including the terminator");
    char concatText[16] = {};
    original_mystrcat(concatText, "F15.spr");
    require(std::strcmp(concatText, "F15.spr") == 0, "original mystrcat appends source text");
    char memsetText[8] = {};
    original_nearmemset(memsetText, 'Z', 3);
    require(std::memcmp(memsetText, "ZZZ\0", 4) == 0, "original nearmemset writes the requested byte count");
    for (auto [value, expected] : {
             std::pair<int, const char *>{0, "0"},
             std::pair<int, const char *>{123, "123"},
             std::pair<int, const char *>{1234, "1,234"},
             std::pair<int, const char *>{-1234, "-1,234"},
         }) {
        char text[16] = {};
        original_my_itoa(value, text);
        require(std::strcmp(text, expected) == 0, "original my_itoa formats signed comma-separated values");
    }
    char pathWithExtension[kReplaceExtensionPathBytes] = {};
    std::strcpy(pathWithExtension, kReplaceExtensionOriginalPath);
    original_replaceExtension(pathWithExtension, kReplaceExtensionNewSuffix);
    require(std::strcmp(pathWithExtension, kReplaceExtensionExpectedPath) == 0,
            "original replaceExtension overwrites the suffix at the first dot");

    /* END map projection keeps only the unsigned byte coordinate, scales by
     * 128, then divides by the original map aspect constants. */
    const int mapCoordSamples[] = {0, 1, 40, 50, 127, 128, 200, 255, 256, -1};
    for (int coord : mapCoordSamples) {
        const auto byteCoord = static_cast<unsigned char>(coord);
        require(original_mapToScreenX(byteCoord) == ((static_cast<int>(byteCoord) << kMapCoordShift) / kMapScaleX),
                "original mapToScreenX matches END integer scaling");
        require(original_mapToScreenY(byteCoord) == ((static_cast<int>(byteCoord) << kMapCoordShift) / kMapScaleY),
                "original mapToScreenY matches END integer scaling");
    }

    auto &nightMission =
        *reinterpret_cast<int16 *>(reinterpret_cast<unsigned char *>(&weaponDataBlock) + kNightMissionWeaponDataOffset);
    for (auto [timeValue, miscBits, target1Type, target2Type] : {
             std::tuple<int, int, int, int>{kFormatFlightDayTime, kFormatFlightDayMiscBits,
                                            kFormatFlightBaseTargetType, kFormatFlightBaseTargetType},
             std::tuple<int, int, int, int>{kFormatFlightNightTime, kFormatFlightNightMiscBits,
                                            kFormatFlightBaseTargetType, kFormatFlightBaseTargetType},
             std::tuple<int, int, int, int>{kFormatFlightForcedTime, kFormatFlightForcedMiscBits,
                                            kFormatFlightDayType, kFormatFlightNightType},
         }) {
        std::memset(&targetBlock, 0, sizeof(targetBlock));
        std::memset(&weaponDataBlock, 0, sizeof(weaponDataBlock));
        targetBlock.target1Type[0] = target1Type;
        targetBlock.target2Type[0] = target2Type;
        targetBlock.target1MiscBits[0] = miscBits;
        char timeText[9] = {};
        require(original_formatFlightTime(timeValue, timeText) == timeText &&
                    std::strcmp(timeText, formatFlightTimeExpected(timeValue, miscBits, target1Type, target2Type).c_str()) == 0 &&
                    nightMission == (timeText[0] == '2' ? 1 : 0),
                "original formatFlightTime applies target bits, night override, and mm:ss arithmetic");
    }

    GameComm endComm = {};
    commData = &endComm;
    worldBufOffset = 0;
    worldBufSegment = 0;
    original_setupWorldBufPtr();
    require(worldBufOffset == static_cast<int16>(FP_OFF(commData) + kWorldBufOffset) &&
                worldBufSegment == static_cast<int16>(FP_SEG(commData)),
            "original setupWorldBufPtr points END world cursor at commData->worldBuf");

    endComm.worldX = kMissionResultGridX << kMissionResultWorldCoordShift;
    endComm.worldY = kMissionResultGridY << kMissionResultWorldCoordShift;
    gridFlags[kMissionResultGridX + kMissionResultGridY * kMissionResultGridStride] = kMissionResultGridFlags;
    missionResult = 0;
    original_computeMissionResult();
    require(missionResult == (kMissionResultGridFlags & kMissionResultMask),
            "original computeMissionResult indexes the 16-wide world grid and keeps low result bits");

    Game endGame = {};
    gameData = &endGame;
    endGame.difficulty = kCalcMissionDifficulty;
    endComm.weaponCount[0] = kCalcMissionRawWeaponCount;
    std::memset(flightDataBuf, 0, sizeof(flightDataBuf));
    samKilled = samMissed = groundKilled = groundMissed = airKilled = airMissed = primaryHit = secondaryHit =
        kCalcMissionCounterSentinel;
    require(original_calcMissionScore(0) == kCalcMissionNoEventScore &&
                samKilled == 0 && samMissed == 0 && groundKilled == 0 && groundMissed == 0 &&
                airKilled == 0 && airMissed == 0 && primaryHit == 0 && secondaryHit == 0,
            "original calcMissionScore resets counters and returns zero when the first record is empty");

    auto *records = reinterpret_cast<FlightRecord *>(flightDataBuf + 2);
    std::memset(flightDataBuf, 0, sizeof(flightDataBuf));
    records[0].status = kCalcMissionPrimaryAirStatus;
    records[0].unitId = kCalcMissionPrimaryAirUnit;
    records[1].status = 0;
    require(original_calcMissionScore(1) == kCalcMissionPrimaryAirScore &&
                airKilled == 1 && primaryHit == 1 && samKilled == 0 && groundKilled == 0,
            "original calcMissionScore caps weapon count at 15 and scores a primary air kill");

    MenuItem hitItem = {};
    hitItem.hitX1 = kDebriefHitX1;
    hitItem.hitY1 = kDebriefHitY1;
    hitItem.hitX2 = kDebriefHitX2;
    hitItem.hitY2 = kDebriefHitY2;
    cursorX = kDebriefCursorInsideX;
    cursorY = kDebriefCursorInsideY;
    require(original_isPointInRect(&hitItem) == 1,
            "original isPointInRect includes points inside the inclusive hit rectangle");
    cursorX = kDebriefCursorOutsideX;
    require(original_isPointInRect(&hitItem) == 0,
            "original isPointInRect rejects points outside the inclusive hit rectangle");

    for (auto [randValue, maxVal] : {std::pair{0, 100}, std::pair{1, 100},
                                     std::pair{16384, 100}, std::pair{32767, 2000},
                                     std::pair{40000, 2000}}) {
        g_randStubValue = randValue;
        const int dosRandValue = randValue & 0x7fff;
        require(original_randomRange(maxVal) == randomRangeFromRand(dosRandValue, maxVal),
                "original randomRange matches fixed implementation for same rand output");
        require(original_randMul(static_cast<std::uint16_t>(maxVal)) == randomRangeFromRand(dosRandValue, maxVal),
                "original start randMul matches fixed implementation for same rand output");
    }

    g_inputDisabled = kReadAxisDisabled;
    g_axisInputAccum[kReadAxisRoll] = kReadAxisIgnoredAccum;
    require(original_readAxisInput(kReadAxisRoll) == kReadAxisDisabledReturn,
            "original readAxisInput returns zero while input is disabled");
    g_inputDisabled = 0;

    for (auto [rangeRaw, expected] : {
             std::pair<int, const char *>{0, "Range 0.0 km"},
             std::pair<int, const char *>{(12 << kRangeKmShift) + 39, "Range 12.6 km"},
             std::pair<int, const char *>{(255 << kRangeKmShift) + kRangeFractionMask, "Range 255.9 km"},
             std::pair<int, const char *>{-1, "Range -1.9 km"},
         }) {
        std::memset(strBuf, 0, sizeof(strBuf));
        std::memset(g_itoaScratch, 0, sizeof(g_itoaScratch));
        original_buildRangeString(rangeRaw);
        require(std::strcmp(strBuf, expected) == 0,
                "original buildRangeString preserves integer km and low-six-bit fraction formatting");
    }
    for (auto [pitch, altitude] : {
             std::pair<int, int>{0, 0},
             std::pair<int, int>{0x1000, 0x2000},
             std::pair<int, int>{-0x1000, 0x2000},
             std::pair<int, int>{0x3000, 0x0100},
             std::pair<int, int>{0x3FFF, 0x4000},
         }) {
        g_ourPitch = static_cast<int16>(pitch);
        g_viewZ = static_cast<int16>(altitude);
        require(original_computeLoftAngle() == loftAngleExpected(pitch, altitude),
                "original computeLoftAngle matches unsigned altitude divide formula");
    }
    g_viewX_ = 5000;
    g_viewY_ = 7000;
    std::memset(matrix3dt, 0, sizeof(matrix3dt));
    std::memset(matrix3dt_2, 0, sizeof(matrix3dt_2));
    std::memset(&nearestTile, 0, sizeof(nearestTile));
    g_nearestTileObj = nullptr;
    require(original_findWaypointEntry(kWaypointLookupMapX, kWaypointLookupMapY) == kWaypointNotFound &&
                g_nearestTileObj == nullptr,
            "original findWaypointEntry returns the no-waypoint sentinel when no nearest tile object exists");

    for (auto [targetX, targetY, wantBearing, initialBearing] : {
             std::tuple<int, int, int, int>{4700, 7600, 1, 0},
             std::tuple<int, int, int, int>{5300, 6400, 0, 0x1234},
         }) {
        const int dx = g_viewX_ - targetX;
        const int dy = g_viewY_ - targetY;
        const int expectedRange = ::rangeApprox(dx, dy);
        const std::uint16_t expectedBearing =
            wantBearing ? f15::fixed::computeBearing(-dx, dy).raw() : static_cast<std::uint16_t>(initialBearing);
        g_targetBearing = static_cast<int16>(initialBearing);
        require(original_computeTargetBearing(targetX, targetY, wantBearing) == expectedRange &&
                    g_targetRange == expectedRange &&
                    static_cast<std::uint16_t>(g_targetBearing) == expectedBearing,
                "original computeTargetBearing writes range and conditionally updates bearing");
    }
    g_planeTable.planes[6].mapX = 4700;
    g_planeTable.planes[6].mapY = 7600;
    require(original_computeMapTargetRange(6) == ::rangeApprox(300, -600) &&
                g_targetRange == ::rangeApprox(300, -600) &&
                static_cast<std::uint16_t>(g_targetBearing) == f15::fixed::computeBearing(-300, -600).raw(),
            "original computeMapTargetRange reads map target coordinates and updates bearing");
    g_targetBearing = 0x1234;
    g_simObjects[3].posX = 4700;
    g_simObjects[3].posY = 7600;
    require(original_computeSimObjectRange(3) == ::rangeApprox(300, -600) &&
                g_targetRange == ::rangeApprox(300, -600) &&
                static_cast<std::uint16_t>(g_targetBearing) == 0x1234,
            "original computeSimObjectRange reads sim-object coordinates without updating bearing");

    g_viewX_ = kThreatViewX;
    g_viewY_ = kThreatViewY;
    g_viewZ = kThreatViewZ;
    g_missionStatus = kThreatMissionStatus;
    int threatBearing = 0;
    int threatRange = 0;
    const int threatDx = kThreatViewX - kThreatX;
    const int threatDy = kThreatViewY - kThreatY;
    const int expectedThreatScore =
        ((kThreatDangerTier + kThreatMissionStatus * kThreatMissionScale + kThreatScoreBase) *
         kThreatLethality / kThreatLethalityDivisor) *
        ((static_cast<unsigned>(kThreatViewZ) >> kThreatAltitudeShift) + kThreatAltitudeBase) >>
        kThreatAltitudeScoreShift;
    require(original_computeThreatRangeBearing(kThreatX, kThreatY, kThreatAltIgnored, kThreatType,
                                               &threatBearing, &threatRange) == expectedThreatScore &&
                threatRange == (::rangeApprox(threatDx, threatDy) >> kRangeKmShift) &&
                static_cast<std::uint16_t>(threatBearing) == f15::fixed::computeBearing(threatDx, -threatDy).raw(),
            "original computeThreatRangeBearing writes range, inverted-Y bearing, and altitude-weighted score");
    require(original_computeThreatRangeBearing(kThreatX, kThreatY, kThreatAltIgnored, kThreatEmptyType,
                                               &threatBearing, &threatRange) == 0 &&
                original_computeThreatRangeBearing(kThreatX, kThreatY, kThreatAltIgnored, kThreatSentinelType,
                                                   &threatBearing, &threatRange) == 0,
            "original computeThreatRangeBearing ignores empty and sentinel threat types");

    g_missionStatus = kThreatScoreMissionStatus;
    g_targetEntityCount = kThreatScoreTargetCount;
    g_planeTable.planes[0].active = kThreatScoreType0;
    g_planeTable.planes[1].active = kThreatScoreType1;
    g_planeTable.planes[2].active = kThreatScoreType2;
    g_planeTable.planes[3].active = kThreatScoreType3;
    int expectedScore = 0;
    for (int activeType : {kThreatScoreType0, kThreatScoreType2, kThreatScoreType3}) {
        expectedScore += aNone[activeType].lethality * aNone[activeType].dangerTier *
                         (kThreatScoreMissionStatus + 2) / kThreatScoreDivisor;
    }
    expectedScore /= kThreatScoreTotalDivisor;
    require(original_computeThreatScore() == expectedScore,
            "original computeThreatScore sums active target threats with original divisors");

    std::memset(g_projectiles, 0, sizeof(g_projectiles));
    g_projectiles[kSamAcquireSlot].mapX = kSamAcquireStartX;
    g_projectiles[kSamAcquireSlot].mapY = kSamAcquireStartY;
    g_projectiles[kSamAcquireSlot].speed = kSamAcquireSpeed;
    g_projectiles[kSamAcquireSlot].worldX = kSamAcquireHeadingEast;
    g_frameRateScaling = kSamAcquireFrameRateScaling;
    require(original_samCanAcquireTarget(kSamAcquireSlot,
                                         kSamAcquireTargetX,
                                         kSamAcquireTargetY,
                                         kSamAcquireTargetAltIgnored,
                                         kSamAcquireModeForward) == 1 &&
                g_acqRange == kSamAcquireExpectedRange &&
                g_acqAimY == kSamAcquireExpectedAim,
            "original samCanAcquireTarget succeeds when projectile can reach target this frame");

    g_playerPlaneFlags = kBombSuppressionFlag;
    g_autopilotEngaged = 0;
    g_bombDamageMask = kBombDamageMaskSentinel;
    g_gunHits = kBombGunHitsSentinel;
    g_damageTakenFlag = kBombDamageTakenSentinel;
    original_bombTarget();
    require(g_bombDamageMask == kBombDamageMaskSentinel &&
                g_gunHits == kBombGunHitsSentinel &&
                g_damageTakenFlag == kBombDamageTakenSentinel,
            "original bombTarget is suppressed when original player-plane flag is set");

    g_waterTargetId[0] = kWaterTargetSymbol;
    g_landTargetId[0] = kLandTargetSymbol;
    g_planeTable.planes[kMapRangeTargetIdx].flags = kTargetIdentifiedFlag;
    g_planeTable.planes[kMapRangeTargetIdx].nameIndex = kTargetSymbolShapeIndex;
    g_shapeTargetCategory[kTargetSymbolShapeIndex] = kWaterTargetCategory;
    require(original_isTargetOverWater(kMapRangeTargetIdx) == 1 &&
                original_getTargetSymbol(kMapRangeTargetIdx) == kWaterTargetSymbol + kIdentifiedSymbolBase,
            "original isTargetOverWater and getTargetSymbol use water-category remap");
    g_shapeTargetCategory[kTargetSymbolShapeIndex] = kLandTargetCategory;
    require(original_isTargetOverWater(kMapRangeTargetIdx) == 0 &&
                original_getTargetSymbol(kMapRangeTargetIdx) == kLandTargetSymbol + kIdentifiedSymbolBase,
            "original getTargetSymbol uses land symbol for non-water identified targets");
    g_planeTable.planes[kMapRangeTargetIdx].flags = 0;
    g_planeTable.planes[kMapRangeTargetIdx].nameIndex = kExplicitTargetSymbol;
    require(original_getTargetSymbol(kMapRangeTargetIdx) == kExplicitTargetSymbol,
            "original getTargetSymbol returns explicit name index when identified flag is clear");

    std::memset(g_camRotMatrix, 0, sizeof(g_camRotMatrix));
    g_camRotMatrix[kRotateVectorAxisX] = kRotateVectorHalfQ14;
    require(original_rotateVectorComponent(kRotateVectorAxisX, kRotateVectorX, kRotateVectorY, kRotateVectorZ) ==
                original_fixedMulQ14(kRotateVectorHalfQ14, kRotateVectorX),
            "original rotateVectorComponent preserves X,Z,Y column access for the selected axis");

    std::cout << "original_fixed_math_compare_tests passed\n";
    return 0;
}
