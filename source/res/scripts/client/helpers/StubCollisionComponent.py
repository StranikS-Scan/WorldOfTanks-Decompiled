# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/StubCollisionComponent.py
import typing
import Math
import CGF
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes

class StubCollisionComponent(object):
    _SIZE = 1.0
    _BBOX_MIN = Math.Vector3(0.0, 0.0, 0.0)
    _BBOX_MAX = Math.Vector3(_SIZE, _SIZE, _SIZE)
    _BBOX_DISTANCE = (_BBOX_MAX - _BBOX_MIN).length
    _NORMAL = Math.Vector3(0, 1, 0)

    def __init__(self, spaceID):
        self._spaceID = spaceID
        self._partIndices = TankPartIndexes.ALL

    @property
    def spaceID(self):
        return self._spaceID

    @property
    def maxStaticPartIndex(self):
        return len(self._partIndices) - 1

    @property
    def partIndices(self):
        return self._partIndices

    def getBoundingBox(self, partIndex):
        return (self._BBOX_MIN, self._BBOX_MAX, self._BBOX_DISTANCE)

    def getPartName(self, partIndex):
        partName = TankPartIndexes.getName(partIndex)
        return partName if partName else TankPartNames.CHASSIS

    def collideLocal(self, partIndex, start, end):
        direction = end - start
        direction.normalise()
        return (0.0,
         Math.Vector3(start),
         Math.Vector3(-direction.x, -direction.y, -direction.z),
         0)

    def collideLocalPoint(self, partIndex, point, maxDistance):
        return (0.0,
         Math.Vector3(point),
         self._NORMAL,
         0)

    def collideAllWorld(self, start, end):
        pass

    def collideShape(self, partIndex, vertices, extent):
        pass

    def collideWorld(self, partIndex, start, end):
        pass

    def collideWorldRecursively(self, partIndex, start, end):
        pass

    def collideLocalRecursively(self, partIndex, start, end):
        pass

    def hasAttachment(self, partIndex):
        return True

    def getParentPartIndex(self, partIndex):
        return None

    def getPartTransform(self, partIndex):
        return Math.Matrix()

    def getPartTransformProvider(self, partIndex):
        return Math.Matrix()

    def getPartGameObject(self, partIndex):
        return CGF.GameObject.INVALID_GAME_OBJECT

    def getColliderID(self):
        pass

    def setOnAttachmentsUpdated(self, callback):
        pass
