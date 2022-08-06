# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/death_zones_mapping.py
import ArenaType
from Math import Vector2
import Math
ZONES_X = 10
ZONES_Y = 10
DEATH_ZONE_IDS = range(0, ZONES_X * ZONES_Y)

def getZoneIdFromPosition(arenaTypeID, position):
    return Math.getZoneIdFromPosition(*(ArenaType.g_cache[arenaTypeID].boundingBox + (position,)))


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
