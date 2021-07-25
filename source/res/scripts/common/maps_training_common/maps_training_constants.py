# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/maps_training_common/maps_training_constants.py
MT_PDATA_KEY = 'mapsTraining'
DEFAULT_PROGRESS_VALUE = 0
MAP_PROGRESS_COMPLETE = 15
MAX_SCENARIO_PROGRESS = 1
VEHICLE_CLASSES_ORDER = ('heavyTank', 'mediumTank', 'lightTank', 'AT-SPG', 'SPG')
PROGRESS_DATA_MASK = 1

class SCENARIO_RESULT:
    LOSE = -1
    PARTIAL = 0
    WIN = 1


class VEHICLE_TYPE:
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    ALL_TYPES = [HEAVY, MEDIUM]
    TEAM1 = 1
    TEAM2 = 2
    ALL_TEAMS = [TEAM1, TEAM2]
    OFFSET = {TEAM1: {HEAVY: 0,
             MEDIUM: 1},
     TEAM2: {HEAVY: 2,
             MEDIUM: 3}}


SCENARIO_ORDER = [(VEHICLE_TYPE.TEAM1, VEHICLE_TYPE.HEAVY),
 (VEHICLE_TYPE.TEAM2, VEHICLE_TYPE.HEAVY),
 (VEHICLE_TYPE.TEAM1, VEHICLE_TYPE.MEDIUM),
 (VEHICLE_TYPE.TEAM2, VEHICLE_TYPE.MEDIUM)]
SCENARIO_INDEXES = {key:i + 1 for i, key in enumerate(SCENARIO_ORDER)}
