# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/common/death_zones_helpers.py
import ArenaType
from Math import Vector2
ZONES_SIZE = 10
DEATH_ZONE_IDS = range(0, ZONES_SIZE * ZONES_SIZE)

class ZONE_STATE(object):
    SAVE = 0
    WARNING = 1
    CRITICAL = 2


class DEATH_ZONES_STRATEGY(object):
    CENTER_DISTANT_FIRST = 0
    LEFT_RIGHT_RANDOM_CHOICE = 1


def idxFrom(zoneId, zoneSize=ZONES_SIZE):
    return (zoneId % zoneSize, zoneId / zoneSize)


def zoneIdFrom(x, y, zoneSize=ZONES_SIZE):
    return y * zoneSize + x


def scale10To(zoneSize, zoneId):
    x, y = idxFrom(zoneId)
    s = zoneSize / ZONES_SIZE
    return (zoneIdFrom(_x, _y, zoneSize) for _x in range(x * s, (x + 1) * s) for _y in range(y * s, (y + 1) * s))


def getZoneIdFromPosition(arenaTypeID, position):
    return _getZoneIdFromPosition(*(ArenaType.g_cache[arenaTypeID].boundingBox + (position, ZONES_SIZE)))


def getZoneIdFromPositionFor(zoneSize, boundbox, position):
    return _getZoneIdFromPosition(*(boundbox + (position, zoneSize)))


def _getZoneIdFromPosition(lowerLeft, upperRight, position, zoneSize):
    x, y = position[0] - lowerLeft[0], position[2] - lowerLeft[1]
    sizeX, sizeY = upperRight - lowerLeft
    x = max(0.0, x)
    y = max(0.0, y)
    return min(int(x / sizeX * zoneSize), zoneSize - 1) + min(int(y / sizeY * zoneSize), zoneSize - 1) * zoneSize


def _getZoneBoundsFromId(arenaTypeID, zoneId, zoneSize, boundbox=None):
    if boundbox is None:
        boundbox = ArenaType.g_cache[arenaTypeID].boundingBox
    lowerLeft, upperRight = boundbox
    lowerLeft = Vector2(*lowerLeft)
    upperRight = Vector2(*upperRight)
    x = zoneId % zoneSize
    y = zoneId / zoneSize
    stepX, stepY = (upperRight - lowerLeft).tuple()
    stepX = stepX / zoneSize
    stepY = stepY / zoneSize
    return (lowerLeft + Vector2(x * stepX, y * stepY), lowerLeft + Vector2((x + 1) * stepX, (y + 1) * stepY))


def getZoneCenterFromId(arenaTypeID, zoneId, boundbox=None):
    lowerLeft, upperRight = _getZoneBoundsFromId(arenaTypeID, zoneId, ZONES_SIZE, boundbox)
    return lowerLeft + (upperRight - lowerLeft) / 2.0


def getZoneCenterFromIdFor(zoneSize, arenaTypeID, zoneId, boundbox=None):
    lowerLeft, upperRight = _getZoneBoundsFromId(arenaTypeID, zoneId, zoneSize, boundbox)
    return lowerLeft + (upperRight - lowerLeft) / 2.0
