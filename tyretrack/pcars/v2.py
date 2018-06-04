import json
import struct

from enum import Enum

from tyretrack.pcars.nationalities import decode_nationality


class EUDPStreamerPacketHandlerType(Enum):
    eCarPhysics = 0
    eRaceDefinition = 1
    eParticipants = 2
    eTimings = 3
    eGameState = 4
    eWeatherState = 5
    eVehicleNames = 6
    eTimeStats = 7
    eParticipantVehicleNames = 8


TYRE_NAME_LENGTH_MAX = 40
TRACKNAME_LENGTH_MAX = 64

PARTICIPANT_NAME_LENGTH_MAX = 64
PARTICIPANTS_PER_PACKET = 16
UDP_STREAMER_PARTICIPANTS_SUPPORTED = 32

VEHICLE_NAME_LENGTH_MAX = 64
CLASS_NAME_LENGTH_MAX = 20
VEHICLES_PER_PACKET = 16
CLASSES_SUPPORTED_PER_PACKET = 60


def decode_base_paket(pkt):
    return {
        'mPacketNumber': struct.unpack_from("<I", pkt, 0)[0],
        'mCategoryPacketNumber': struct.unpack_from("<I", pkt, 4)[0],

        'mPartialPacketIndex': struct.unpack_from("<B", pkt, 8)[0],
        'mPartialPacketNumber': struct.unpack_from("<B", pkt, 9)[0],
        'mPacketType': EUDPStreamerPacketHandlerType(struct.unpack_from("<B", pkt, 10)[0]),
        'mPacketVersion': struct.unpack_from("<B", pkt, 11)[0],
    }


def decode_telemetry_data(pkt, sBase):
    data = {
        # Participant info
        'sViewedParticipantIndex': struct.unpack_from("<b", pkt, 12)[0],
        # Unfiltered input
        'sUnfilteredThrottle': struct.unpack_from("<B", pkt, 13)[0],
        'sUnfilteredBrake': struct.unpack_from("<B", pkt, 14)[0],
        'sUnfilteredSteering': struct.unpack_from("<b", pkt, 15)[0],
        'sUnfilteredClutch': struct.unpack_from("<B", pkt, 16)[0],
        # Car state
        'sCarFlags': struct.unpack_from("<B", pkt, 17)[0],
        'sOilTempCelsius': struct.unpack_from("<h", pkt, 18)[0],
        'sOilPressureKPa': struct.unpack_from("<H", pkt, 20)[0],
        'sWaterTempCelsius': struct.unpack_from("<h", pkt, 22)[0],
        'sWaterPressureKpa': struct.unpack_from("<H", pkt, 24)[0],
        'sFuelPressureKpa': struct.unpack_from("<H", pkt, 26)[0],
        'sFuelCapacity': struct.unpack_from("<B", pkt, 28)[0],
        'sBrake': struct.unpack_from("<B", pkt, 29)[0],
        'sThrottle': struct.unpack_from("<B", pkt, 30)[0],
        'sClutch': struct.unpack_from("<B", pkt, 31)[0],
        'sFuelLevel': struct.unpack_from("<f", pkt, 32)[0],
        'sSpeed': struct.unpack_from("<f", pkt, 36)[0],
        'sRpm': struct.unpack_from("<H", pkt, 40)[0],
        'sMaxRpm': struct.unpack_from("<H", pkt, 42)[0],
        'sSteering': struct.unpack_from("<b", pkt, 44)[0],
        'sGearNumGears': struct.unpack_from("<B", pkt, 45)[0],
        'sBoostAmount': struct.unpack_from("<B", pkt, 46)[0],
        'sCrashState': struct.unpack_from("<B", pkt, 47)[0],

        'sOdometerKM': struct.unpack_from("<f", pkt, 48),
        'sOrientation': struct.unpack_from("<fff", pkt, 52),
        'sLocalVelocity': struct.unpack_from("<fff", pkt, 64),
        'sWorldVelocity': struct.unpack_from("<fff", pkt, 76),
        'sAngularVelocity': struct.unpack_from("<fff", pkt, 88),
        'sLocalAcceleration': struct.unpack_from("<fff", pkt, 100),
        'sWorldAcceleration': struct.unpack_from("<fff", pkt, 112),
        'sExtentsCentre': struct.unpack_from("<fff", pkt, 124),

        'sTyreFlags': struct.unpack_from("<BBBB", pkt, 136),
        'sTerrain': struct.unpack_from("<BBBB", pkt, 140),
        'sTyreY': struct.unpack_from("<ffff", pkt, 144),
        'sTyreRPS': struct.unpack_from("<ffff", pkt, 160),

        'sTyreTemp': struct.unpack_from("<BBBB", pkt, 176),
        'sTyreHeightAboveGround': struct.unpack_from("<ffff", pkt, 180),
        'sTyreWear': struct.unpack_from("<BBBB", pkt, 196),
        'sBrakeDamage': struct.unpack_from("<BBBB", pkt, 200),
        'sSuspensionDamage': struct.unpack_from("<BBBB", pkt, 204),
        'sBrakeTempCelsius': struct.unpack_from("<hhhh", pkt, 208),
        'sTyreTreadTemp': struct.unpack_from("<HHHH", pkt, 216),
        'sTyreLayerTemp': struct.unpack_from("<HHHH", pkt, 224),
        'sTyreCarcassTemp': struct.unpack_from("<HHHH", pkt, 240),
        'sTyreRimTemp': struct.unpack_from("<HHHH", pkt, 248),

        'sTyreTempLeft': struct.unpack_from("<HHHH", pkt, 256),
        'sTyreTempCenter': struct.unpack_from("<HHHH", pkt, 264),
        'sTyreTempRight': struct.unpack_from("<HHHH", pkt, 272),

        'sWheelLocalPositionY': struct.unpack_from("<ffff", pkt, 280),
        'sRideHeight': struct.unpack_from("<ffff", pkt, 296),
        'sSuspensionTravel': struct.unpack_from("<ffff", pkt, 312),
        'sSuspensionVelocity': struct.unpack_from("<ffff", pkt, 328),
        'sSuspensionRideHeight': struct.unpack_from("<HHHH", pkt, 344),

        'sAirPressure': struct.unpack_from("<HHHH", pkt, 352),

        'sEngineSpeed': struct.unpack_from("<f", pkt, 360)[0],
        'sEngineTorque': struct.unpack_from("<f", pkt, 264)[0],

        'sWings': struct.unpack_from("<BB", pkt, 368),
        'sHandbrake': struct.unpack_from("<B", pkt, 370)[0],

        'sAeroDamage': struct.unpack_from("<B", pkt, 371)[0],
        'sEngineDamage': struct.unpack_from("<B", pkt, 372)[0],

        'sJoyPad0': struct.unpack_from("<I", pkt, 376)[0],
        'sDPad': struct.unpack_from("<B", pkt, 377)[0],

        'sTyreCompound': list(map(lambda s: s.split(b'\x00')[0].decode('utf-8'), struct.unpack_from(
            f"<{TYRE_NAME_LENGTH_MAX}s{TYRE_NAME_LENGTH_MAX}s{TYRE_NAME_LENGTH_MAX}s{TYRE_NAME_LENGTH_MAX}s", pkt,
            378))),

        'sTurboBoostPressure': struct.unpack_from("<f", pkt, 538)[0],
        'sFullPosition': struct.unpack_from("<fff", pkt, 542)[0],
        'sBrakeBias': struct.unpack_from("<B", pkt, 554)[0],
        'sTickCount': struct.unpack_from("<I", pkt, 555)[0],
    }

    return data


def decode_race_data(pkt, sBase):
    data = {
        'sWorldFastestLapTime': struct.unpack_from("<f", pkt, 12)[0],
        'sPersonalFastestLapTime': struct.unpack_from("<f", pkt, 16)[0],
        'sPersonalFastestSector1Time': struct.unpack_from("<f", pkt, 20)[0],
        'sPersonalFastestSector2Time': struct.unpack_from("<f", pkt, 24)[0],
        'sPersonalFastestSector3Time': struct.unpack_from("<f", pkt, 28)[0],
        'sWorldFastestSector1Time': struct.unpack_from("<f", pkt, 32)[0],
        'sWorldFastestSector2Time': struct.unpack_from("<f", pkt, 36)[0],
        'sWorldFastestSector3Time': struct.unpack_from("<f", pkt, 40)[0],
        'sTrackLength': struct.unpack_from("<f", pkt, 44)[0],
        'sTrackLocation': struct.unpack_from(f"<{TRACKNAME_LENGTH_MAX}s", pkt, 48)[0].split(b'\x00')[0].decode('utf-8'),
        'sTrackVariation': struct.unpack_from(f"<{TRACKNAME_LENGTH_MAX}s", pkt, 112)[0].split(b'\x00')[0].decode(
            'utf-8'),
        'sTranslatedTrackLocation': struct.unpack_from(f"<{TRACKNAME_LENGTH_MAX}s", pkt, 176)[0].split(b'\x00')[
            0].decode('utf-8'),
        'sTranslatedTrackVariation': struct.unpack_from(f"<{TRACKNAME_LENGTH_MAX}s", pkt, 240)[0].split(b'\x00')[
            0].decode('utf-8'),
        'sLapsTimeInEvent': struct.unpack_from("<H", pkt, 304)[0],
        'sEnforcedPitStopLap': struct.unpack_from("<b", pkt, 306)[0],
    }

    if data['sLapsTimeInEvent'] & 0x8000:
        data['sLapsInEvent'] = 0
        data['sTimeInEvent'] = 5 * (data['sLapsTimeInEvent'] & 0x7FFF)
    else:
        data['sLapsInEvent'] = data['sLapsTimeInEvent'] & 0x7FFF
        data['sTimeInEvent'] = 0

    # del data['sLapsTimeInEvent']

    return data


def decode_game_data(pkt, sBase):
    data = {
        'mBuildVersionNumber': struct.unpack_from("<h", pkt, 12)[0],
        'mGameState': struct.unpack_from("<B", pkt, 15)[0],
        'sAmbientTemperature': struct.unpack_from("<b", pkt, 16)[0],
        'sTrackTemperature': struct.unpack_from("<b", pkt, 17)[0],
        'sRainDensity': struct.unpack_from("<B", pkt, 18)[0],
        'sSnowDensity': struct.unpack_from("<B", pkt, 19)[0],
        'sWindSpeed': struct.unpack_from("<b", pkt, 20)[0],
        'sWindDirectionX': struct.unpack_from("<b", pkt, 21)[0],
        'sWindDirectionY': struct.unpack_from("<b", pkt, 22)[0],
    }

    data['sGameState'] = \
        ['GAME_EXITED',
         'GAME_FRONT_END',
         'GAME_INGAME_PLAYING',
         'GAME_INGAME_PAUSED',
         'GAME_INGAME_INMENU_TIME_TICKING',
         'GAME_INGAME_RESTARTING',
         'GAME_INGAME_REPLAY',
         'GAME_FRONT_END_REPLAY',
         ][data['mGameState'] & 7]
    data['sSessionState'] = \
        ['SESSION_INVALID',
         'SESSION_PRACTICE',
         'SESSION_TEST',
         'SESSION_QUALIFY',
         'SESSION_FORMATION_LAP',
         'SESSION_RACE',
         'SESSION_TIME_ATTACK',
         ][data['mGameState'] >> 3]
    # del data['mGameState']

    return data


def decode_participant_info(pkt, offset, num):
    sParticipantInfo = []
    for i in range(1, num):
        info = {
            'sWorldPosition': struct.unpack_from("<hhh", pkt, offset),
            'sOrientation': struct.unpack_from("<hhh", pkt, offset + 6),
            'sCurrentLapDistance': struct.unpack_from("<H", pkt, offset + 12)[0],
            'sRacePosition': struct.unpack_from("<B", pkt, offset + 14)[0],
            'sSector': struct.unpack_from("<B", pkt, offset + 15)[0],
            'sHighestFlag': struct.unpack_from("<B", pkt, offset + 16)[0],
            'sPitModeSchedule': struct.unpack_from("<B", pkt, offset + 17)[0],
            'sCarIndex': struct.unpack_from("<H", pkt, offset + 18)[0],
            'sRaceState': struct.unpack_from("<B", pkt, offset + 20)[0],
            'sCurrentLap': struct.unpack_from("<B", pkt, offset + 21)[0],
            'sCurrentTime': struct.unpack_from("<f", pkt, offset + 22)[0],
            'sCurrentSectorTime': struct.unpack_from("<f", pkt, offset + 26)[0],
            'sMPParticipantIndex': struct.unpack_from("<H", pkt, offset + 30)[0]
        }

        info['sIsActive'] = (info['sRacePosition'] | 0x80) == 0x80
        info['sRacePosition'] &= 0x7F

        info['sIsHuman'] = (info['sCarIndex'] | 0x8000) == 0x8000
        info['sCarIndex'] &= 0x7FFF

        info['sInvalidatedLap'] = (info['sRaceState'] & 8) == 8
        info['sRaceState'] = [
            'RACESTATE_INVALID',
            'RACESTATE_NOT_STARTED',
            'RACESTATE_RACING',
            'RACESTATE_FINISHED',
            'RACESTATE_DISQUALIFIED',
            'RACESTATE_RETIRED',
            'RACESTATE_DNF',
        ][info['sRaceState'] & 7]

        info['sCurrentSector'] = info['sSector'] & 3
        sign0 = 4 if info['sWorldPosition'][0] >= 0 else -4
        sign2 = 4 if info['sWorldPosition'][2] >= 0 else -4
        info['sWorldPosition'] = (
            info['sWorldPosition'][0] + (info['sSector'] >> 6) / sign0,
            info['sWorldPosition'][1],
            info['sWorldPosition'][2] + (info['sSector'] >> 4 & 3) / sign2
        )
        del info['sSector']

        info['sHighestFlagReason'] = [
            'FLAG_REASON_NONE ',
            'FLAG_REASON_SOLO_CRASH',
            'FLAG_REASON_VEHICLE_CRASH',
            'FLAG_REASON_VEHICLE_OBSTRUCTION',
        ][info['sHighestFlag'] >> 4]

        info['sHighestFlagColour'] = [
            'FLAG_COLOUR_NONE',
            'FLAG_COLOUR_GREEN',
            'FLAG_COLOUR_BLUE',
            'FLAG_COLOUR_WHITE_SLOW_CAR',
            'FLAG_COLOUR_WHITE_FINAL_LAP',
            'FLAG_COLOUR_RED',
            'FLAG_COLOUR_YELLOW',
            'FLAG_COLOUR_DOUBLE_YELLOW',
            'FLAG_COLOUR_BLACK_AND_WHITE',
            'FLAG_COLOUR_BLACK_ORANGE_CIRCLE',
            'FLAG_COLOUR_BLACK',
            'FLAG_COLOUR_CHEQUERED',
        ][info['sHighestFlag'] & 0x0f]

        info['sPitMode'] = [
            'PIT_MODE_NONE ',
            'PIT_MODE_DRIVING_INTO_PITS',
            'PIT_MODE_IN_PIT',
            'PIT_MODE_DRIVING_OUT_OF_PITS',
            'PIT_MODE_IN_GARAGE',
            'PIT_MODE_DRIVING_OUT_OF_GARAGE',
        ][info['sPitModeSchedule'] & 0x0f]

        info['sPitSchedule'] = [
            'PIT_SCHEDULE_NONE',
            'PIT_SCHEDULE_PLAYER_REQUESTED',
            'PIT_SCHEDULE_ENGINEER_REQUESTED',
            'PIT_SCHEDULE_DAMAGE_REQUESTED',
            'PIT_SCHEDULE_MANDATORY',
            'PIT_SCHEDULE_DRIVE_THROUGH',
            'PIT_SCHEDULE_STOP_GO',
            'PIT_SCHEDULE_PITSPOT_OCCUPIED',
        ][info['sPitModeSchedule'] >> 4]

        sParticipantInfo.append(info)
        offset += 32

    return sParticipantInfo


def decode_timings_data(pkt, sBase):
    data = {
        'sNumParticipants': struct.unpack_from("<b", pkt, 12)[0],
        'sParticipantsChangedTimestamp': struct.unpack_from("<I", pkt, 13)[0],
        'sEventTimeRemaining': struct.unpack_from("<f", pkt, 17)[0],
        'sSplitTimeAhead': struct.unpack_from("<f", pkt, 21)[0],
        'sSplitTimeBehind': struct.unpack_from("<f", pkt, 25)[0],
        'sSplitTime': struct.unpack_from("<f", pkt, 29)[0],
        'sLocalParticipantIndex': struct.unpack_from("<H", pkt, 1057)[0],
        'sTickCount': struct.unpack_from("<I", pkt, 1059)[0],
    }

    data['sParticipantInfo'] = decode_participant_info(pkt, 33, data['sNumParticipants'])

    return data


def decode_participant_stats(pkt, offset, num):
    sParticipantStats = []
    for i in range(1, num):
        info = {
            'sFastestLapTime': struct.unpack_from("<f", pkt, offset)[0],
            'sLastLapTime': struct.unpack_from("<f", pkt, offset + 4)[0],
            'sLastSectorTime': struct.unpack_from("<f", pkt, offset + 8)[0],
            'sFastestSector1Time': struct.unpack_from("<f", pkt, offset + 11)[0],
            'sFastestSector2Time': struct.unpack_from("<f", pkt, offset + 16)[0],
            'sFastestSector3Time': struct.unpack_from("<f", pkt, offset + 20)[0],
            'sParticipantOnlineRep': struct.unpack_from("<I", pkt, offset + 24)[0],
            'sMPParticipantIndex': struct.unpack_from("<H", pkt, offset + 28)[0],
        }

        sParticipantStats.append(info)
        offset += 32

    return sParticipantStats


def decode_timings_stats_data(pkt, sBase):
    return {
        'sParticipantsChangedTimestamp': struct.unpack_from("<I", pkt, 12)[0],
        'sParticipantsStats': decode_participant_stats(pkt, 33, UDP_STREAMER_PARTICIPANTS_SUPPORTED)
    }


def decode_particpants(pkt):
    sParticipants = []
    for i in range(0, PARTICIPANTS_PER_PACKET - 1):
        info = {
            'sName': struct.unpack_from(f"<{PARTICIPANT_NAME_LENGTH_MAX}s", pkt, 16 + 64 * i)[0].split(b'\x00')[
                0].decode('utf-8'),
            'sNationality': decode_nationality(struct.unpack_from("<I", pkt, 1040 + 4 * i)[0]),
            'sIndex': struct.unpack_from("<H", pkt, 1104 + 2 * i)[0],
        }

        sParticipants.append(info)
    return sParticipants


def decode_particpant_data(pkt, sBase):
    return {
        'sParticipantsChangedTimestamp': struct.unpack_from("<I", pkt, 12)[0],
        'sParticipants': decode_particpants(pkt)
    }


def decode_vehicle_info(pkt, offset):
    sVehicles = []
    for i in range(1, VEHICLES_PER_PACKET):
        info = {
            'sIndex': struct.unpack_from("<H", pkt, offset)[0],
            'sClass': struct.unpack_from("<I", pkt, offset + 2)[0],
            'padding': struct.unpack_from("<H", pkt, offset + 6)[0],
            'sName': struct.unpack_from(f"<{VEHICLE_NAME_LENGTH_MAX}s", pkt, offset + 8)[0].split(b'\x00')[0].decode(
                'utf-8'),
        }

        sVehicles.append(info)
        offset += 72

    return sVehicles


def decode_participant_vehicle_names(pkt, sBase):
    data = {}
    if len(pkt) == 1164:
        data = {
            'sVehicleInfo': decode_vehicle_info(pkt, offset=12)
        }
    elif len(pkt) == 1452:
        data = {
            'sClassInfo': decode_class_info(pkt, offset=12)
        }
    print(len(pkt), sBase, data)
    return data


def decode_class_info(pkt, offset):
    sClasses = []
    for i in range(1, CLASSES_SUPPORTED_PER_PACKET):
        info = {
            'sClassIndex': struct.unpack_from("<H", pkt, offset)[0],
            'sName': struct.unpack_from(f"<{CLASS_NAME_LENGTH_MAX}s", pkt, offset + 4)[0].split(b'\x00')[0].decode(
                'utf-8'),
        }

        sClasses.append(info)
        offset += 24

    return sClasses


def decode_vehicle_names(pkt, sBase):
    data = {
        'sClassInfo': decode_class_info(pkt, offset=12)
    }
    return data


def decode(pkt):
    decoded = decode_base_paket(pkt)

    decoders = {
        EUDPStreamerPacketHandlerType.eCarPhysics: decode_telemetry_data,
        EUDPStreamerPacketHandlerType.eRaceDefinition: decode_race_data,
        EUDPStreamerPacketHandlerType.eGameState: decode_game_data,
        EUDPStreamerPacketHandlerType.eTimings: decode_timings_data,
        EUDPStreamerPacketHandlerType.eTimeStats: decode_timings_stats_data,
        EUDPStreamerPacketHandlerType.eParticipants: decode_particpant_data,
        EUDPStreamerPacketHandlerType.eParticipantVehicleNames: decode_participant_vehicle_names,
    }
    if decoded['mPacketType'] not in decoders:
        print('Unkown packet', decoded['mPacketType'])
        return False, None

    fun = decoders[decoded['mPacketType']]

    data = fun(pkt, decoded)

    decoded.update(data)

    # if decoded['mPacketType'] != EUDPStreamerPacketHandlerType.eCarPhysics and decoded[
    #    'mPacketType'] != EUDPStreamerPacketHandlerType.eTimings:
    #    print(decoded)

    return False, None
