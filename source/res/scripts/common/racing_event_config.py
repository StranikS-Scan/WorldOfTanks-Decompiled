# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/racing_event_config.py
from bonus_readers import timeDataToUTC
RACING_LAST_POSITION = 127

class RaceTokens(object):
    RACE_ATTEMPT_TOKEN = 'fest19:race:attempt'
    RACE_RESTORE_ATTEMPTS_TOKEN = 'fest19:race:restore'
    RACE_TOKEN_EXPIRE = timeDataToUTC('08.04.2020 03:00')
    RACE_POINTS_TOKEN = 'fest19:race:leg_all:points'
    RACE_POINTS_LEG_TOKENS = ('fest19:race:leg_1:points', 'fest19:race:leg_2:points', 'fest19:race:leg_3:points', 'fest19:race:leg_4:points', 'fest19:race:leg_5:points')
    RACE_TEAM_1_TOKEN = 'fest19:race:team_a'
    RACE_TEAM_2_TOKEN = 'fest19:race:team_b'
    RACE_TEAM_3_TOKEN = 'fest19:race:team_c'
    RACE_TEAM_TOKENS = (RACE_TEAM_1_TOKEN, RACE_TEAM_2_TOKEN, RACE_TEAM_3_TOKEN)


class RacingTeams(object):
    OUT_OF_TEAM, TEAM_1, TEAM_2, TEAM_3 = range(4)
    ALL = (OUT_OF_TEAM,
     TEAM_1,
     TEAM_2,
     TEAM_3)


RACING_TEAM_BY_TOKEN_NAME = {RaceTokens.RACE_TEAM_1_TOKEN: RacingTeams.TEAM_1,
 RaceTokens.RACE_TEAM_2_TOKEN: RacingTeams.TEAM_2,
 RaceTokens.RACE_TEAM_3_TOKEN: RacingTeams.TEAM_3}

class RacingVehicles(object):
    VEHICLE_1 = 64001
    VEHICLE_2 = 64529
    VEHICLE_3 = 62497
    ALL = (VEHICLE_1, VEHICLE_2, VEHICLE_3)


class RacingToogleReason(object):
    START = 1
    PAUSE = 2
    RESUME = 3
    STOP = 4


class VehicleProperties(object):
    SPEED = 'speed'
    ACCELERATION = 'acceleration'
    CHASSIS_HANDLING = 'chassis_handling'
    DPM = 'dpm'
    GUN_RELOAD = 'gun_reload'
    ARMOR = 'armor'


class PrepertyValue(object):
    HIGH = 'high'
    MIDDLE = 'middle'
    LOW = 'low'


RACING_VEHICLES_PROPERTIES = {RacingVehicles.VEHICLE_1: {VehicleProperties.SPEED: ('100', True),
                            VehicleProperties.ACCELERATION: ('2', False),
                            VehicleProperties.CHASSIS_HANDLING: (PrepertyValue.HIGH, True),
                            VehicleProperties.DPM: ('22', False),
                            VehicleProperties.GUN_RELOAD: ('1.5', True),
                            VehicleProperties.ARMOR: ('1000', False)},
 RacingVehicles.VEHICLE_2: {VehicleProperties.SPEED: ('120', True),
                            VehicleProperties.ACCELERATION: ('3.5', False),
                            VehicleProperties.CHASSIS_HANDLING: (PrepertyValue.LOW, False),
                            VehicleProperties.DPM: ('6(x12)', True),
                            VehicleProperties.GUN_RELOAD: ('5', False),
                            VehicleProperties.ARMOR: ('1000', False)},
 RacingVehicles.VEHICLE_3: {VehicleProperties.SPEED: ('110', False),
                            VehicleProperties.ACCELERATION: ('3', False),
                            VehicleProperties.CHASSIS_HANDLING: (PrepertyValue.MIDDLE, False),
                            VehicleProperties.DPM: ('40', True),
                            VehicleProperties.GUN_RELOAD: ('3', False),
                            VehicleProperties.ARMOR: ('1000', False)}}
