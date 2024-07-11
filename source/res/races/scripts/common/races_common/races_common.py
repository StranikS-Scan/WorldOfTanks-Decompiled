# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/common/races_common/races_common.py
import enum

def checkIfViolator(avatarResults):
    fairplayState = avatarResults.get('fairplayViolations', (0, 0, 0))
    return fairplayState[1] != 0


@enum.unique
class RacesImpulseType(enum.IntEnum):
    RAM = 1
    SHOT = 2
    BOOST = 3
    BOUNDARY = 5


@enum.unique
class RacesScoreEvents(enum.IntEnum):
    SHOT = 1
    RAMMING = 2
    ELECTRICAL_SHOCK = 3
    BOOST = 4
    SHIELD = 5
    POWER_IMPULSE = 6
    FINISH = 7


@enum.unique
class RacesShotType(enum.IntEnum):
    DEFAULT = 1
    RAPID = 2


@enum.unique
class RacesAbilities(enum.IntEnum):
    RAPID_SHOT = 1
