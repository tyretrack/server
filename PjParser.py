 import struct


def readParticipantInfo(pkt, offset, num):
    sParticipantInfo = []
    for i in range(1, num):
        info = {
            'sWorldPosition': struct.unpack_from("<hhh", pkt, offset),
            'sCurrentLapDistance': struct.unpack_from("<H", pkt, offset + 6)[0],
            'sRacePosition': struct.unpack_from("<B", pkt, offset + 8)[0],
            'sLapsCompleted': struct.unpack_from("<B", pkt, offset + 9)[0],
            'sCurrentLap': struct.unpack_from("<B", pkt, offset + 10)[0],
            'sSector': struct.unpack_from("<B", pkt, offset + 11)[0],
            'sLastSectorTime': struct.unpack_from("<f", pkt, offset + 12)[0],
        }

        info['sIsActive'] = (info['sRacePosition'] | 128) == 128
        info['sRacePosition'] &= 127

        info['sLapInvalidated'] = (info['sLapsCompleted'] | 128) == 128
        info['sLapsCompleted'] &= 127

        info['sCurrentSector'] = info['sSector'] & 7
        sign0 = 4 if info['sWorldPosition'][0] >= 0 else -4
        sign2 = 4 if info['sWorldPosition'][2] >= 0 else -4
        info['sWorldPosition'] = (
            info['sWorldPosition'][0] + (info['sSector'] >> 6) / sign0,
            info['sWorldPosition'][1],
            info['sWorldPosition'][2] + (info['sSector'] >> 4 & 3) / sign2
        )
        del info['sSector']

        sParticipantInfo.append(info)
        offset += 16

    return sParticipantInfo


def decodeTelemetryData(pkt):
    data = {
        'sBuildVersionNumber': struct.unpack_from("<h", pkt, 0)[0],
        'sPacketType': struct.unpack_from("<B", pkt, 2)[0],

        'sGameSessionState': struct.unpack_from("<B", pkt, 3)[0],

        'sViewedParticipantIndex': struct.unpack_from("<b", pkt, 4)[0],
        'sNumParticipants': struct.unpack_from("<b", pkt, 5)[0],

        'sUnfilteredThrottle': struct.unpack_from("<B", pkt, 6)[0],
        'sUnfilteredBrake': struct.unpack_from("<B", pkt, 7)[0],
        'sUnfilteredSteering': struct.unpack_from("<b", pkt, 8)[0],
        'sUnfilteredClutch': struct.unpack_from("<B", pkt, 9)[0],
        'sRaceStateFlags': struct.unpack_from("<B", pkt, 10)[0],

        'sLapsInEvent': struct.unpack_from("<B", pkt, 11)[0],

        'sBestLapTime': struct.unpack_from("<f", pkt, 12)[0],
        'sLastLapTime': struct.unpack_from("<f", pkt, 16)[0],
        'sCurrentTime': struct.unpack_from("<f", pkt, 20)[0],
        'sSplitTimeAhead': struct.unpack_from("<f", pkt, 24)[0],
        'sSplitTimeBehind': struct.unpack_from("<f", pkt, 28)[0],
        'sSplitTime': struct.unpack_from("<f", pkt, 32)[0],
        'sEventTimeRemaining': struct.unpack_from("<f", pkt, 36)[0],
        'sPersonalFastestLapTime': struct.unpack_from("<f", pkt, 40)[0],
        'sWorldFastestLapTime': struct.unpack_from("<f", pkt, 44)[0],
        'sCurrentSector1Time': struct.unpack_from("<f", pkt, 48)[0],
        'sCurrentSector2Time': struct.unpack_from("<f", pkt, 52)[0],
        'sCurrentSector3Time': struct.unpack_from("<f", pkt, 56)[0],
        'sFastestSector1Time': struct.unpack_from("<f", pkt, 60)[0],
        'sFastestSector2Time': struct.unpack_from("<f", pkt, 64)[0],
        'sFastestSector3Time': struct.unpack_from("<f", pkt, 68)[0],
        'sPersonalFastestSector1Time': struct.unpack_from("<f", pkt, 72)[0],
        'sPersonalFastestSector2Time': struct.unpack_from("<f", pkt, 76)[0],
        'sPersonalFastestSector3Time': struct.unpack_from("<f", pkt, 80)[0],
        'sWorldFastestSector1Time': struct.unpack_from("<f", pkt, 84)[0],
        'sWorldFastestSector2Time': struct.unpack_from("<f", pkt, 88)[0],
        'sWorldFastestSector3Time': struct.unpack_from("<f", pkt, 92)[0],

        'sJoyPad': struct.unpack_from("<h", pkt, 96)[0],

        'sHighestFlag': struct.unpack_from("<B", pkt, 98)[0],

        'sPitModeSchedule': struct.unpack_from("<B", pkt, 99)[0],

        'sOilTempCelsius': struct.unpack_from("<h", pkt, 100)[0],
        'sOilPressureKPa': struct.unpack_from("<H", pkt, 102)[0],
        'sWaterTempCelsius': struct.unpack_from("<h", pkt, 104)[0],
        'sWaterPressureKpa': struct.unpack_from("<H", pkt, 106)[0],
        'sFuelPressureKpa': struct.unpack_from("<H", pkt, 108)[0],
        'sCarFlags': struct.unpack_from("<B", pkt, 110)[0],
        'sFuelCapacity': struct.unpack_from("<B", pkt, 111)[0],
        'sBrake': struct.unpack_from("<B", pkt, 112)[0],
        'sThrottle': struct.unpack_from("<B", pkt, 113)[0],
        'sClutch': struct.unpack_from("<B", pkt, 114)[0],
        'sSteering': struct.unpack_from("<b", pkt, 115)[0],
        'sFuelLevel': struct.unpack_from("<f", pkt, 116)[0],
        'sSpeed': struct.unpack_from("<f", pkt, 120)[0],
        'sRpm': struct.unpack_from("<H", pkt, 124)[0],
        'sMaxRpm': struct.unpack_from("<H", pkt, 126)[0],
        'sGearNumGears': struct.unpack_from("<B", pkt, 128)[0],
        'sBoostAmount': struct.unpack_from("<B", pkt, 129)[0],
        'sEnforcedPitStopLap': struct.unpack_from("<b", pkt, 130)[0],
        'sCrashState': struct.unpack_from("<B", pkt, 131)[0],

        'sOdometerKM': struct.unpack_from("<f", pkt, 132),
        'sOrientation': struct.unpack_from("<fff", pkt, 136),
        'sLocalVelocity': struct.unpack_from("<fff", pkt, 148),
        'sWorldVelocity': struct.unpack_from("<fff", pkt, 160),
        'sAngularVelocity': struct.unpack_from("<fff", pkt, 172),
        'sLocalAcceleration': struct.unpack_from("<fff", pkt, 184),
        'sWorldAcceleration': struct.unpack_from("<fff", pkt, 196),
        'sExtentsCentre': struct.unpack_from("<fff", pkt, 208),

        'sTyreFlags': struct.unpack_from("<BBBB", pkt, 220),
        'sTerrain': struct.unpack_from("<BBBB", pkt, 224),
        'sTyreY': struct.unpack_from("<ffff", pkt, 228),
        'sTyreRPS': struct.unpack_from("<ffff", pkt, 244),
        'sTyreSlipSpeed': struct.unpack_from("<ffff", pkt, 260),
        'sTyreTemp': struct.unpack_from("<BBBB", pkt, 276),
        'sTyreGrip': struct.unpack_from("<BBBB", pkt, 280),
        'sTyreHeightAboveGround': struct.unpack_from("<ffff", pkt, 284),
        'sTyreLateralStiffness': struct.unpack_from("<ffff", pkt, 300),
        'sTyreWear': struct.unpack_from("<BBBB", pkt, 316),
        'sBrakeDamage': struct.unpack_from("<BBBB", pkt, 320),
        'sSuspensionDamage': struct.unpack_from("<BBBB", pkt, 324),
        'sBrakeTempCelsius': struct.unpack_from("<hhhh", pkt, 328),
        'sTyreTreadTemp': struct.unpack_from("<HHHH", pkt, 336),
        'sTyreLayerTemp': struct.unpack_from("<HHHH", pkt, 344),
        'sTyreCarcassTemp': struct.unpack_from("<HHHH", pkt, 352),
        'sTyreRimTemp': struct.unpack_from("<HHHH", pkt, 360),
        'sTyreInternalAirTemp': struct.unpack_from("<HHHH", pkt, 368),
        'sWheelLocalPositionY': struct.unpack_from("<ffff", pkt, 376),
        'sRideHeight': struct.unpack_from("<ffff", pkt, 392),
        'sSuspensionTravel': struct.unpack_from("<ffff", pkt, 408),
        'sSuspensionVelocity': struct.unpack_from("<ffff", pkt, 424),
        'sAirPressure': struct.unpack_from("<HHHH", pkt, 440),

        'sEngineSpeed': struct.unpack_from("<f", pkt, 448)[0],
        'sEngineTorque': struct.unpack_from("<f", pkt, 452)[0],

        'sAeroDamage': struct.unpack_from("<B", pkt, 456)[0],
        'sEngineDamage': struct.unpack_from("<B", pkt, 457)[0],

        'sAmbientTemperature': struct.unpack_from("<b", pkt, 458)[0],
        'sTrackTemperature': struct.unpack_from("<b", pkt, 459)[0],
        'sRainDensity': struct.unpack_from("<B", pkt, 460)[0],
        'sWindSpeed': struct.unpack_from("<b", pkt, 461)[0],
        'sWindDirectionX': struct.unpack_from("<b", pkt, 462)[0],
        'sWindDirectionY': struct.unpack_from("<b", pkt, 463)[0],

        'sTrackLength': struct.unpack_from("<f", pkt, 1360)[0],
        'sWings': struct.unpack_from("<BB", pkt, 1364),
        'sDPad': struct.unpack_from("<B", pkt, 1366)[0],
    }

    data['sParticipationInfo'] = readParticipantInfo(pkt, 464, min(data['sNumParticipants'] + 1, 56))

    data['sCount'] = data['sPacketType'] >> 2
    data['sPacketType'] &= 2 ** 2 - 1

    data['sGameState'] = \
        ['GAME_EXITED',
         'GAME_FRONT_END',
         'GAME_INGAME_PLAYING',
         'GAME_INGAME_PAUSED',
         'GAME_INGAME_RESTART'][data['sGameSessionState'] & 7]
    data['sSessionState'] = \
        ['SESSION_INVALID',
         'SESSION_PRACTICE',
         'SESSION_TEST',
         'SESSION_QUALIFY',
         'SESSION_FORMATION_LAP',
         'SESSION_RACE',
         'SESSION_TIME_ATTACK'][data['sGameSessionState'] >> 4]
    del data['sGameSessionState']

    data['sRaceState'] = \
        ['RACESTATE_INVALID',
         'RACESTATE_NOT_STARTED',
         'RACESTATE_RACING',
         'RACESTATE_FINISHED',
         'RACESTATE_DISQUALIFIED',
         'RACESTATE_RETIRED',
         'RACESTATE_DNF'][data['sRaceStateFlags'] & 2 ** 3 - 1]
    data['sLapInvalidated'] = data['sRaceStateFlags'] & 8 == 8
    data['sAntiLockActive'] = data['sRaceStateFlags'] & 16 == 16
    data['sBoostActive'] = data['sRaceStateFlags'] & 32 == 32
    del data['sRaceStateFlags']

    data['sHighestFlagColor'] = [
        'FLAG_COLOUR_NONE',
        'FLAG_COLOUR_GREEN',
        'FLAG_COLOUR_BLUE',
        'FLAG_COLOUR_WHITE',
        'FLAG_COLOUR_YELLOW',
        'FLAG_COLOUR_DOUBLE_YELLOW',
        'FLAG_COLOUR_BLACK',
        'FLAG_COLOUR_CHEQUERED',
    ][data['sHighestFlag'] & 2 ** 4 - 1]
    data['sHighestFlagReason'] = [
        'FLAG_REASON_NONE',
        'FLAG_REASON_SOLO_CRASH',
        'FLAG_REASON_VEHICLE_CRASH',
        'FLAG_REASON_VEHICLE_OBSTRUCTION',
    ][data['sHighestFlag'] >> 4]
    del data['sHighestFlag']

    data['sPitMode'] = \
        ['PIT_MODE_NON',
         'PIT_MODE_DRIVING_INTO_PITS',
         'PIT_MODE_IN_PIT',
         'PIT_MODE_DRIVING_OUT_OF_PITS',
         'PIT_MODE_IN_GARAGE'][data['sPitModeSchedule'] & 2 ** 4 - 1]
    data['sPitSchedule'] = [
        'PIT_SCHEDULE_NONE0',
        'PIT_SCHEDULE_STANDARD',
        'PIT_SCHEDULE_DRIVE_THROUGH',
        'PIT_SCHEDULE_STOP_GO',
    ][data['sPitModeSchedule'] >> 4]
    del data['sPitModeSchedule']

    data['sGear'] = data['sGearNumGears'] & 2 ** 4 - 1
    data['sNumGears'] = data['sGearNumGears'] >> 4
    del data['sGearNumGears']

    data['sHeadlight'] = data['sCarFlags'] & 1 == 1
    data['sEngineActive'] = data['sCarFlags'] & 2 == 2
    data['sEngineWarning'] = data['sCarFlags'] & 4 == 4
    data['sSpeedLimiter'] = data['sCarFlags'] & 8 == 8
    data['sABS'] = data['sCarFlags'] & 16 == 16
    data['sHandbrake'] = data['sCarFlags'] & 32 == 32
    data['sStability'] = data['sCarFlags'] & 64 == 64
    data['sTractionControl'] = data['sCarFlags'] & 128 == 128

    TERRAIN_FLAGS = [
        'TERRAIN_ROAD',
        'TERRAIN_LOW_GRIP_ROAD',
        'TERRAIN_BUMPY_ROAD1',
        'TERRAIN_BUMPY_ROAD2',
        'TERRAIN_BUMPY_ROAD3',
        'TERRAIN_MARBLES',
        'TERRAIN_GRASSY_BERMS',
        'TERRAIN_GRASS',
        'TERRAIN_GRAVEL',
        'TERRAIN_BUMPY_GRAVEL',
        'TERRAIN_RUMBLE_STRIPS',
        'TERRAIN_DRAINS',
        'TERRAIN_TYREWALLS',
        'TERRAIN_CEMENTWALLS',
        'TERRAIN_GUARDRAILS',
        'TERRAIN_SAND',
        'TERRAIN_BUMPY_SAND',
        'TERRAIN_DIRT',
        'TERRAIN_BUMPY_DIRT',
        'TERRAIN_DIRT_ROAD',
        'TERRAIN_BUMPY_DIRT_ROAD',
        'TERRAIN_PAVEMENT',
        'TERRAIN_DIRT_BANK',
        'TERRAIN_WOOD',
        'TERRAIN_DRY_VERGE',
        'TERRAIN_EXIT_RUMBLE_STRIPS',
        'TERRAIN_GRASSCRETE',
        'TERRAIN_LONG_GRASS',
        'TERRAIN_SLOPE_GRASS',
        'TERRAIN_COBBLES',
        'TERRAIN_SAND_ROAD',
        'TERRAIN_BAKED_CLAY',
        'TERRAIN_ASTROTURF',
        'TERRAIN_SNOWHALF',
        'TERRAIN_SNOWFULL',
    ]
    data['sTerrain'] = (
        TERRAIN_FLAGS[data['sTerrain'][0]],
        TERRAIN_FLAGS[data['sTerrain'][1]],
        TERRAIN_FLAGS[data['sTerrain'][2]],
        TERRAIN_FLAGS[data['sTerrain'][3]],
    )

    data['sTyreFlags'] = (
        {'Attached': data['sTyreFlags'][0] & 1 == 1,
         'Inflated': data['sTyreFlags'][0] & 2 == 2,
         'OnTheGround': data['sTyreFlags'][0] & 4 == 4},
        {'Attached': data['sTyreFlags'][1] & 1 == 1,
         'Inflated': data['sTyreFlags'][1] & 2 == 2,
         'OnTheGround': data['sTyreFlags'][1] & 4 == 4},
        {'Attached': data['sTyreFlags'][2] & 1 == 1,
         'Inflated': data['sTyreFlags'][2] & 2 == 2,
         'OnTheGround': data['sTyreFlags'][2] & 4 == 4},
        {'Attached': data['sTyreFlags'][3] & 1 == 1,
         'Inflated': data['sTyreFlags'][3] & 2 == 2,
         'OnTheGround': data['sTyreFlags'][3] & 4 == 4},
    )

    data['sCrashState'] = [
        'CRASH_DAMAGE_NONE',
        'CRASH_DAMAGE_OFFTRACK',
        'CRASH_DAMAGE_LARGE_PROP',
        'CRASH_DAMAGE_SPINNING',
        'CRASH_DAMAGE_ROLLING',
    ][data['sCrashState']]

    return data


def parseNames(pkt, offset, num):
    sNames = []
    for i in range(1, num):
        sNames.append(struct.unpack_from("<64s", pkt, offset)[0].split(b'\x00')[0].decode("iso-8859-1"))
        offset += 64
    return sNames


def decodeParticipantInfoStrings(pkt):
    data = {
        'sBuildVersionNumber': struct.unpack_from("<h", pkt, 0)[0],
        'sPacketType': struct.unpack_from("<B", pkt, 2)[0],
        'sCarName': struct.unpack_from("<64s", pkt, 3)[0].split(b'\x00')[0].decode("iso-8859-1"),
        'sTrackLocation': struct.unpack_from("<64s", pkt, 131)[0].split(b'\x00')[0].decode("iso-8859-1"),
        'sTrackVariation': struct.unpack_from("<64s", pkt, 195)[0].split(b'\x00')[0].decode("iso-8859-1"),
        'sPlayerName': struct.unpack_from("<64s", pkt, 259)[0].split(b'\x00')[0].decode("iso-8859-1"),
        'sName': parseNames(pkt, 323, 16),
    }

    data['sCount'] = data['sPacketType'] >> 2
    data['sPacketType'] &= 3

    return data


def decodeParticipantInfoStringsAdditional(pkt):
    data = {
        'sBuildVersionNumber': struct.unpack_from("<h", pkt, 0)[0],
        'sPacketType': struct.unpack_from("<B", pkt, 2)[0],
        'sOffset': struct.unpack_from("<B", pkt, 3)[0],
        'sName': parseNames(pkt, 4, 16),
    }

    data['sCount'] = data['sPacketType'] >> 2
    data['sPacketType'] &= 3

    return data


def decode(pkt):
    length = len(pkt)
    if length == 1367:
        return True, decodeTelemetryData(pkt)
    elif length == 1347:
        return True, decodeParticipantInfoStrings(pkt)
    elif length == 1028:
        return True, decodeParticipantInfoStringsAdditional(pkt)
    else:
        print('Unkown packet with length: ' + str(length))
        return False, {}
