# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/death_zones_mapping.py
import ArenaType
from Math import Vector2
ZONES_X = 10
ZONES_Y = 10
DEATH_ZONE_IDS = range(0, ZONES_X * ZONES_Y)

def getZoneIdFromPosition(arenaTypeID, position):
    return _getZoneIdFromPosition(*(ArenaType.g_cache[arenaTypeID].boundingBox + (position,)))


def _getZoneIdFromPosition(lowerLeft, upperRight, position):
    x, y = position[0] - lowerLeft[0], position[2] - lowerLeft[1]
    sizeX, sizeY = upperRight - lowerLeft
    x = max(0.0, x)
    y = max(0.0, y)
    return min(int(x / sizeX * ZONES_X), ZONES_X - 1) + min(int(y / sizeY * ZONES_Y), ZONES_Y - 1) * ZONES_X


def getZoneBoundsFromId(arenaTypeID, zoneId):
    lowerLeft, upperRight = ArenaType.g_cache[arenaTypeID].boundingBox
    lowerLeft = Vector2(*lowerLeft)
    upperRight = Vector2(*upperRight)
    x = zoneId % ZONES_X
    y = zoneId / ZONES_X
    stepX, stepY = (upperRight - lowerLeft).tuple()
    stepX = stepX / ZONES_X
    stepY = stepY / ZONES_Y
    return (lowerLeft + Vector2(x * stepX, y * stepY), lowerLeft + Vector2((x + 1) * stepX, (y + 1) * stepY))


def getZoneCenterFromId(arenaTypeID, zoneId):
    lowerLeft, upperRight = getZoneBoundsFromId(arenaTypeID, zoneId)
    return lowerLeft + (upperRight - lowerLeft) / 2.0
