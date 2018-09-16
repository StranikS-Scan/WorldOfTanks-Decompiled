# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/entries.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.battle_control.battle_constants import VEHICLE_LOCATION
from gui.shared.utils.decorators import ReprInjector

class MinimapEntry(object):
    __slots__ = ('_entryID', '_isActive', '_matrix')

    def __init__(self, entryID, active, matrix=None):
        super(MinimapEntry, self).__init__()
        self._entryID = entryID
        self._isActive = active
        self._matrix = matrix

    def getID(self):
        return self._entryID

    def getMatrix(self):
        return self._matrix

    def setMatrix(self, matrix):
        self._matrix = matrix
        return True

    def isActive(self):
        return self._isActive

    def setActive(self, active):
        if self._isActive != active:
            self._isActive = active
            return True
        return False

    def clear(self):
        self._entryID = 0
        self._isActive = False
        self._matrix = None
        return


@ReprInjector.simple(('_entryID', 'id'), ('_isActive', 'active'), ('_isInAoI', 'AoI'), ('_isEnemy', 'enemy'), ('_classTag', 'class'))
class VehicleEntry(MinimapEntry):
    __slots__ = ('_entryID', '_classTag', '_location', '_guiLabel', '_spottedCount', '_spottedTime', '_isInAoI', '_isEnemy', '_isAlive')

    def __init__(self, entryID, active, matrix=None, location=VEHICLE_LOCATION.UNDEFINED):
        super(VehicleEntry, self).__init__(entryID, active, matrix=matrix)
        self._isInAoI = False
        self._isEnemy = True
        self._classTag = None
        self._guiLabel = ''
        self._isAlive = True
        self._location = location
        if active:
            self._spottedCount = 1
            self._spottedTime = BigWorld.serverTime()
        else:
            self._spottedCount = 0
            self._spottedTime = None
        return

    def isEnemy(self):
        return self._isEnemy

    def getClassTag(self):
        return self._classTag

    def setVehicleInfo(self, isEnemy, guiLabel, classTag, isAlive):
        self._isEnemy = isEnemy
        self._classTag = classTag
        self._guiLabel = guiLabel
        self._isAlive = isAlive
        return True

    def getGUILabel(self):
        return self._guiLabel

    def setGUILabel(self, guiLabel):
        if self._guiLabel != guiLabel:
            self._guiLabel = guiLabel
            return True
        return False

    def isAlive(self):
        return self._isAlive

    def setAlive(self, isAlive):
        if self._isAlive != isAlive:
            self._isAlive = isAlive
            return self._isActive
        return False

    def getLocation(self):
        return self._location

    def setLocation(self, location):
        self._location = location
        return True

    def isInAoI(self):
        return self._isInAoI

    def setInAoI(self, isInAoI):
        if self._isInAoI != isInAoI:
            self._isInAoI = isInAoI
            if self._isInAoI:
                if self._classTag == 'SPG':
                    self._spottedTime = BigWorld.serverTime()
                self._spottedCount += 1
            elif self._classTag != 'SPG':
                self._spottedTime = BigWorld.serverTime()
            return True
        else:
            return False

    def updatePosition(self, position):
        self._matrix.source.setTranslate(position)

    def wasSpotted(self):
        return not self._isInAoI and self._matrix is not None

    def getActualSpottedCount(self):
        expiryTime = BigWorld.serverTime() + settings.MINIMAP_WAS_SPOTTED_RESET_DELAY
        if self._spottedTime is not None and self._spottedTime <= expiryTime:
            if self._isInAoI and self._isActive:
                self._spottedCount = 1
            else:
                self._spottedCount = 0
        return self._spottedCount

    def getSpottedAnimation(self, pool):
        animation = ''
        if self._isEnemy and self._isActive and self._isInAoI:
            if self._classTag == 'SPG':
                if self.getActualSpottedCount() == 1:
                    animation = 'enemySPG'
            else:
                count = 0
                for entry in pool:
                    if entry.getID() == self._entryID or not entry.isEnemy() or not entry.isInAoI():
                        continue
                    count += entry.getActualSpottedCount()

                if not count:
                    animation = 'firstEnemy'
        return animation
