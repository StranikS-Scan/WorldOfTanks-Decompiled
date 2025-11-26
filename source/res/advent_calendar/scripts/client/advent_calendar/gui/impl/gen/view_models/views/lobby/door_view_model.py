# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/gen/view_models/views/lobby/door_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class DoorState(Enum):
    CLOSED = 'closed'
    OPENED = 'opened'
    READY_TO_OPEN = 'readyToOpen'
    EXPIRED = 'expired'


class Mark(Enum):
    NONE = 'none'
    NY = 'ny'
    NY_EVENT = 'nyEvent'
    WDR = 'wdr'


class DoorViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(DoorViewModel, self).__init__(properties=properties, commands=commands)

    def getDayId(self):
        return self._getNumber(0)

    def setDayId(self, value):
        self._setNumber(0, value)

    def getDoorState(self):
        return DoorState(self._getString(1))

    def setDoorState(self, value):
        self._setString(1, value.value)

    def getMark(self):
        return Mark(self._getString(2))

    def setMark(self, value):
        self._setString(2, value.value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getOpenTimeStamp(self):
        return self._getNumber(4)

    def setOpenTimeStamp(self, value):
        self._setNumber(4, value)

    def getIsEnoughResources(self):
        return self._getBool(5)

    def setIsEnoughResources(self, value):
        self._setBool(5, value)

    def getOpenAnimationRequired(self):
        return self._getBool(6)

    def setOpenAnimationRequired(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(DoorViewModel, self)._initialize()
        self._addNumberProperty('dayId', 0)
        self._addStringProperty('doorState', DoorState.CLOSED.value)
        self._addStringProperty('mark', Mark.NONE.value)
        self._addNumberProperty('price', 0)
        self._addNumberProperty('openTimeStamp', 0)
        self._addBoolProperty('isEnoughResources', False)
        self._addBoolProperty('openAnimationRequired', False)
