# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common/cosmic_event_common.py
import enum

@enum.unique
class ScoreEvents(enum.IntEnum):
    SHOT = 1
    RAMMING = 2
    KILL = 3
    PICKUP = 4
    ABILITY_HIT = 5
    ARTIFACT_SCAN = 6


@enum.unique
class ImpulseType(enum.IntEnum):
    RAM = 1
    SHOT = 2
    BOOSTER = 3
    BLACKHOLE = 4
    BOUNDARY = 5


@enum.unique
class Abilities(enum.IntEnum):
    BLACK_HOLE = 1
    GRAVITY_FIELD = 2
    SNIPER_SHOT = 3
    POWER_SHOT = 4


@enum.unique
class ArtifactComponentStages(enum.IntEnum):
    ANNOUNCEMENT = 1
    SCANNING = 2


def checkIfViolator(avatarResults):
    fairplayState = avatarResults.get('fairplayViolations', (0, 0, 0))
    return fairplayState[1] != 0
