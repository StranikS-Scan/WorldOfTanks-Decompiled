# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/minimap_utils.py
import math
import string
import BigWorld
import Math
from constants import AOI
AOI_TO_FAR_TIME = 5.0
MINIMAP_SIZE = (210.0, 210.0)
EPIC_MINIMAP_HIT_AREA = 210
_METERS_TO_KILOMETERS = 0.001
if AOI.ENABLE_MANUAL_RULES:
    AOI_ESTIMATE = AOI.VEHICLE_CIRCULAR_AOI_RADIUS - 50.0

    def isVehicleInAOI(matrix):
        ownPos = Math.Matrix(BigWorld.camera().invViewMatrix).translation
        entryPos = Math.Matrix(matrix).translation
        return (ownPos.x - entryPos.x) ** 2 + (ownPos.z - entryPos.z) ** 2 < AOI_ESTIMATE ** 2


else:
    AOI_ESTIMATE = 450.0

    def isVehicleInAOI(matrix):
        ownPos = Math.Matrix(BigWorld.camera().invViewMatrix).translation
        entryPos = Math.Matrix(matrix).translation
        return bool(abs(ownPos.x - entryPos.x) < AOI_ESTIMATE and abs(ownPos.z - entryPos.z) < AOI_ESTIMATE)


def getPositionByLocal(localX, localY, bottomLeft, upperRight):
    spaceSize = upperRight - bottomLeft
    x = (localX - MINIMAP_SIZE[0] * 0.5) / MINIMAP_SIZE[0] * spaceSize[0]
    z = -((localY - MINIMAP_SIZE[1] * 0.5) / MINIMAP_SIZE[1]) * spaceSize[1]
    return (x, 0.0, z)


def makePositionMatrix(position):
    matrix = Math.Matrix()
    matrix.setTranslate(position)
    return matrix


def makePointInBBoxMatrix(position, bottomLeft, upperRight):
    vector2 = (upperRight + bottomLeft) * 0.5
    matrix = Math.Matrix()
    matrix.setTranslate((vector2.x, 0.0, vector2.y))
    vector3 = matrix.applyPoint(position)
    matrix.setTranslate(vector3)
    return matrix


def makePointMatrixByLocal(localX, localY, bottomLeft, upperRight):
    return makePointInBBoxMatrix(getPositionByLocal(localX, localY, bottomLeft, upperRight), bottomLeft, upperRight)


def metersToMinimapPixels(minSize, maxSize):
    mmPixelsWidth, mmPixelsHeight = MINIMAP_SIZE
    mapWidthPx = int(abs(maxSize[0] - minSize[0]) * _METERS_TO_KILOMETERS * mmPixelsWidth)
    mapHeightPx = int(abs(maxSize[1] - minSize[1]) * _METERS_TO_KILOMETERS * mmPixelsHeight)
    return (mapWidthPx, mapHeightPx)


def getCellIdFromPosition(desiredShotPoint, boundingBox, dimensions):
    mapXLength = boundingBox[1][0] - boundingBox[0][0]
    mapYLength = boundingBox[1][1] - boundingBox[0][1]
    xOffset = -boundingBox[0][0]
    yOffset = -boundingBox[0][1]
    mapGridX = math.floor((xOffset + desiredShotPoint.x) / mapXLength * dimensions)
    mapGridY = math.floor((yOffset - desiredShotPoint.z) / mapYLength * dimensions)
    return mapGridX * dimensions + mapGridY


def getCellName(cellId, dimensions):
    column, row = divmod(int(cellId), int(dimensions))
    if row < 8:
        name = string.ascii_uppercase[row]
    else:
        name = string.ascii_uppercase[row + 1]
    return '{}{}'.format(name, int((column + 1) % dimensions))
