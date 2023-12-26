# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/advent_calendar_door_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class DoorState(Enum):
    CLOSED = 'closed'
    OPENED = 'opened'
    READY_TO_OPEN = 'readyToOpen'
    EXPIRED = 'expired'


class AdventCalendarDoorViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(AdventCalendarDoorViewModel, self).__init__(properties=properties, commands=commands)

    def getDayId(self):
        return self._getNumber(0)

    def setDayId(self, value):
        self._setNumber(0, value)

    def getDoorState(self):
        return DoorState(self._getString(1))

    def setDoorState(self, value):
        self._setString(1, value.value)

    def getPrice(self):
        return self._getNumber(2)

    def setPrice(self, value):
        self._setNumber(2, value)

    def getOpenTimeStamp(self):
        return self._getNumber(3)

    def setOpenTimeStamp(self, value):
        self._setNumber(3, value)

    def getIsEnoughResources(self):
        return self._getBool(4)

    def setIsEnoughResources(self, value):
        self._setBool(4, value)

    def getOpenAnimationRequired(self):
        return self._getBool(5)

    def setOpenAnimationRequired(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(AdventCalendarDoorViewModel, self)._initialize()
        self._addNumberProperty('dayId', 0)
        self._addStringProperty('doorState', DoorState.CLOSED.value)
        self._addNumberProperty('price', 0)
        self._addNumberProperty('openTimeStamp', 0)
        self._addBoolProperty('isEnoughResources', False)
        self._addBoolProperty('openAnimationRequired', False)
