# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/tooltips/entry_point_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EventState(Enum):
    NOTSTARTED = 'notStarted'
    FORBIDDEN = 'forbidden'
    PAUSED = 'paused'
    REGULARREWARDAVAILABLE = 'regularRewardAvailable'
    TOPREWARDAVAILABLE = 'topRewardAvailable'
    NOREWARDS = 'noRewards'
    REGULARREWARDRECEIVED = 'regularRewardReceived'
    TOPREWARDRECEIVED = 'topRewardReceived'


class EntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(EntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getTimeLeft(self):
        return self._getNumber(3)

    def setTimeLeft(self, value):
        self._setNumber(3, value)

    def getIsEventEndingSoon(self):
        return self._getBool(4)

    def setIsEventEndingSoon(self, value):
        self._setBool(4, value)

    def getRewardCount(self):
        return self._getNumber(5)

    def setRewardCount(self, value):
        self._setNumber(5, value)

    def getEventState(self):
        return EventState(self._getString(6))

    def setEventState(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(EntryPointTooltipModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isEventEndingSoon', False)
        self._addNumberProperty('rewardCount', 0)
        self._addStringProperty('eventState')
