# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/entries.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.battle_control.battle_constants import VEHICLE_LOCATION
from gui.shared.utils.decorators import ReprInjector

class MinimapEntry(object):
    """
    Base class of that holds information about entry on the minimap.
    """
    __slots__ = ('_entryID', '_isActive', '_matrix')

    def __init__(self, entryID, active, matrix=None):
        super(MinimapEntry, self).__init__()
        self._entryID = entryID
        self._isActive = active
        self._matrix = matrix

    def getID(self):
        """
        Gets unique ID of entry.
        :return: number containing ID.
        """
        return self._entryID

    def getMatrix(self):
        """
        Gets matrix.
        :return: instance of MatrixProvider or None.
        """
        return self._matrix

    def setMatrix(self, matrix):
        """
        Sets matrix.
        :param matrix: instance of MatrixProvider.
        :return: True if property is changed, otherwise - False.
        """
        self._matrix = matrix
        return True

    def isActive(self):
        """
        Is entry active.
        :return: bool
        """
        return self._isActive

    def setActive(self, active):
        """
        Sets active. Entry is shown/hidden on the minimap.
        :param active: bool.
        :return: True if property is changed, otherwise - False.
        """
        if self._isActive != active:
            self._isActive = active
            return True
        return False

    def clear(self):
        """
        Clears data.
        """
        self._entryID = 0
        self._isActive = False
        self._matrix = None
        return


@ReprInjector.simple(('_entryID', 'id'), ('_isActive', 'active'), ('_isInAoI', 'AoI'), ('_isEnemy', 'enemy'), ('_classTag', 'class'))
class VehicleEntry(MinimapEntry):
    """
    Class that holds information about vehicle's entry.
    """
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
        """
        Is vehicle enemy.
        :return: bool.
        """
        return self._isEnemy

    def getClassTag(self):
        """
        Gets class of vehicle.
        :return:
        """
        return self._classTag

    def setVehicleInfo(self, isEnemy, guiLabel, classTag, isAlive):
        """
        Sets information about vehicle.
        :param isEnemy: bool, is vehicle enemy.
        :param guiLabel: string containing GUI label of entry.
            There are available values: ally, enemy, teamKiller, squadman.
        :param classTag: string containing class of vehicle.
            There are available values: lightTank, mediumTank, heavyTank, SPG,
            AT-SPG.
        :param isAlive: bool, is vehicle alive.
        :return: True if object is changed, otherwise - False.
        """
        self._isEnemy = isEnemy
        self._classTag = classTag
        self._guiLabel = guiLabel
        self._isAlive = isAlive
        return True

    def getGUILabel(self):
        """
        Gets GUI label.
        :return: string containing GUI label of entry.
        """
        return self._guiLabel

    def setGUILabel(self, guiLabel):
        """
        Sets GUI label.
        :param guiLabel: string containing GUI label of entry.
        :return: True if property is changed, otherwise - False.
        """
        if self._guiLabel != guiLabel:
            self._guiLabel = guiLabel
            return True
        return False

    def isAlive(self):
        """
        Is vehicle alive.
        :return: bool.
        """
        return self._isAlive

    def setAlive(self, isAlive):
        """
        Set vehicle alive.
        :param isAlive: is vehicle alive.
        :return: True if property is changed and entry is active,
            otherwise - False.
        """
        if self._isAlive != isAlive:
            self._isAlive = isAlive
            return self._isActive
        return False

    def getLocation(self):
        """
        Gets vehicle location
        :return: one of VEHICLE_LOCATION.
        """
        return self._location

    def setLocation(self, location):
        """
        Sets location.
        :param location: one of VEHICLE_LOCATION.
        :return: True if property is changed, otherwise - False.
        """
        self._location = location
        return True

    def isInAoI(self):
        """
        Is vehicle in area of interactive.
        :return: bool.
        """
        return self._isInAoI

    def setInAoI(self, isInAoI):
        """
        Set vehicle in area of interactive.
        :param isInAoI: bool.
        :return: True if property is changed, otherwise - False.
        """
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
        """
        Update vehicle position if vehicle location is translated by radio.
        :param position:
        :return:
        """
        assert self._location == VEHICLE_LOCATION.FAR
        self._matrix.source.setTranslate(position)

    def wasSpotted(self):
        """
        Vehicle was spotted and still is not visible.
        :return: bool.
        """
        return not self._isInAoI and self._matrix is not None

    def getActualSpottedCount(self):
        """
        Update count of spotted if time is expired.
        :return: integer containing updated count of spotted.
        """
        expiryTime = BigWorld.serverTime() + settings.MINIMAP_WAS_SPOTTED_RESET_DELAY
        if self._spottedTime is not None and self._spottedTime <= expiryTime:
            if self._isInAoI and self._isActive:
                self._spottedCount = 1
            else:
                self._spottedCount = 0
        return self._spottedCount

    def getSpottedAnimation(self, pool):
        """
        Gets name of animation when vehicle has been added to AoI at first
        time or by some special rules.
        
        :param pool: references to pool.
        :return: string containing name of animation or empty.
        """
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
