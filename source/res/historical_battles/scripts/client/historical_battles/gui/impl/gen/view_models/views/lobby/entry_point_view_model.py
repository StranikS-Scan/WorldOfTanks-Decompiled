# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/entry_point_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class EventState(Enum):
    ANNOUNCE = 'announce'
    ACTIVE = 'active'
    BANNED = 'banned'


class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class EntryPointViewModel(ViewModel):
    __slots__ = ('onClick', 'onShowingAnimationFinish')

    def __init__(self, properties=4, commands=2):
        super(EntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getEventState(self):
        return EventState(self._getString(0))

    def setEventState(self, value):
        self._setString(0, value.value)

    def getTimeLeft(self):
        return self._getNumber(1)

    def setTimeLeft(self, value):
        self._setNumber(1, value)

    def getIsAnimated(self):
        return self._getBool(2)

    def setIsAnimated(self, value):
        self._setBool(2, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(3))

    def setPerformanceRisk(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(EntryPointViewModel, self)._initialize()
        self._addStringProperty('eventState')
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isAnimated', False)
        self._addStringProperty('performanceRisk')
        self.onClick = self._addCommand('onClick')
        self.onShowingAnimationFinish = self._addCommand('onShowingAnimationFinish')
