# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/markers/grinch_progression_marker_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MarkerState(Enum):
    LOCK = 'lock'
    ACTIVE = 'active'
    PAUSED = 'paused'
    DONE = 'done'


class GrinchProgressionMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(GrinchProgressionMarkerModel, self).__init__(properties=properties, commands=commands)

    def getCountdown(self):
        return self._getNumber(0)

    def setCountdown(self, value):
        self._setNumber(0, value)

    def getPoints(self):
        return self._getNumber(1)

    def setPoints(self, value):
        self._setNumber(1, value)

    def getPrevPoints(self):
        return self._getNumber(2)

    def setPrevPoints(self, value):
        self._setNumber(2, value)

    def getIsVisible(self):
        return self._getBool(3)

    def setIsVisible(self, value):
        self._setBool(3, value)

    def getEnoughForClaimReward(self):
        return self._getBool(4)

    def setEnoughForClaimReward(self, value):
        self._setBool(4, value)

    def getMarkerState(self):
        return MarkerState(self._getString(5))

    def setMarkerState(self, value):
        self._setString(5, value.value)

    def getSyncInitiator(self):
        return self._getNumber(6)

    def setSyncInitiator(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(GrinchProgressionMarkerModel, self)._initialize()
        self._addNumberProperty('countdown', 0)
        self._addNumberProperty('points', 0)
        self._addNumberProperty('prevPoints', 0)
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('enoughForClaimReward', False)
        self._addStringProperty('markerState', MarkerState.LOCK.value)
        self._addNumberProperty('syncInitiator', 0)
