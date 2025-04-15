# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/tooltips/entry_point_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from resource_well.gui.impl.gen.view_models.views.lobby.enums import EventMode
from frameworks.wulf import ViewModel
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.reward_info_model import RewardInfoModel

class EventState(Enum):
    NOT_STARTED = 'NOT_STARTED'
    FORBIDDEN = 'FORBIDDEN'
    PAUSED = 'PAUSED'
    IN_PROGRESS = 'IN_PROGRESS'


class EntryPointTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(EntryPointTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getTimeLeft(self):
        return self._getNumber(2)

    def setTimeLeft(self, value):
        self._setNumber(2, value)

    def getIsEventEndingSoon(self):
        return self._getBool(3)

    def setIsEventEndingSoon(self, value):
        self._setBool(3, value)

    def getEventState(self):
        return EventState(self._getString(4))

    def setEventState(self, value):
        self._setString(4, value.value)

    def getEventMode(self):
        return EventMode(self._getString(5))

    def setEventMode(self, value):
        self._setString(5, value.value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return RewardInfoModel

    def _initialize(self):
        super(EntryPointTooltipModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isEventEndingSoon', False)
        self._addStringProperty('eventState')
        self._addStringProperty('eventMode')
        self._addArrayProperty('rewards', Array())
