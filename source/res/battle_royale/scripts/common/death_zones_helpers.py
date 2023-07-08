# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/common/death_zones_helpers.py
import ArenaType
from Math import Vector2
ZONES_X = 10
ZONES_Y = 10
DEATH_ZONE_IDS = range(0, ZONES_X * ZONES_Y)

class ZONE_STATE(object):
    SAVE = 0
    WARNING = 1
    CRITICAL = 2


class DEATH_ZONES_STRATEGY(object):
    CENTER_DISTANT_FIRST = 0
    LEFT_RIGHT_RANDOM_CHOICE = 1


def idxFrom(zoneId):
    return (zoneId % ZONES_X, zoneId / ZONES_X)


def zoneIdFrom(x, y):
    return y * ZONES_X + x


def getZoneIdFromPosition(arenaTypeID, position):
    return _getZoneIdFromPosition(*(ArenaType.g_cache[arenaTypeID].boundingBox + (position,)))


def _getZoneIdFromPosition(lowerLeft, upperRight, position):
    x, y = position[0] - lowerLeft[0], position[2] - lowerLeft[1]
    sizeX, sizeY = upperRight - lowerLeft
    x = max(0.0, x)
    y = max(0.0, y)
    return min(int(x / sizeX * ZONES_X), ZONES_X - 1) + min(int(y / sizeY * ZONES_Y), ZONES_Y - 1) * ZONES_X


def getZoneBoundsFromId(arenaTypeID, zoneId, boundbox=None):
    if boundbox is None:
        boundbox = ArenaType.g_cache[arenaTypeID].boundingBox
    lowerLeft, upperRight = boundbox
    lowerLeft = Vector2(*lowerLeft)
    upperRight = Vector2(*upperRight)
    x = zoneId % ZONES_X
    y = zoneId / ZONES_X
    stepX, stepY = (upperRight - lowerLeft).tuple()
    stepX = stepX / ZONES_X
    stepY = stepY / ZONES_Y
    return (lowerLeft + Vector2(x * stepX, y * stepY), lowerLeft + Vector2((x + 1) * stepX, (y + 1) * stepY))


def getZoneCenterFromId(arenaTypeID, zoneId, boundbox=None):
    lowerLeft, upperRight = getZoneBoundsFromId(arenaTypeID, zoneId, boundbox)
    return lowerLeft + (upperRight - lowerLeft) / 2.0
