# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/event_banner_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class State(Enum):
    INTRO = 'intro'
    INPROGRESS = 'inProgress'
    FROZEN = 'frozen'
    INANNOUNCEMENT = 'inAnnouncement'


class EventBannerViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=8, commands=1):
        super(EventBannerViewModel, self).__init__(properties=properties, commands=commands)

    def getDate(self):
        return self._getNumber(0)

    def setDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getIsNew(self):
        return self._getBool(2)

    def setIsNew(self, value):
        self._setBool(2, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(3))

    def setPerformanceRisk(self, value):
        self._setString(3, value.value)

    def getMaxProgressionStep(self):
        return self._getNumber(4)

    def setMaxProgressionStep(self, value):
        self._setNumber(4, value)

    def getFinishedLevelsCount(self):
        return self._getNumber(5)

    def setFinishedLevelsCount(self, value):
        self._setNumber(5, value)

    def getNextTimeEnable(self):
        return self._getNumber(6)

    def setNextTimeEnable(self, value):
        self._setNumber(6, value)

    def getState(self):
        return State(self._getString(7))

    def setState(self, value):
        self._setString(7, value.value)

    def _initialize(self):
        super(EventBannerViewModel, self)._initialize()
        self._addNumberProperty('date', 0)
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('isNew', False)
        self._addStringProperty('performanceRisk')
        self._addNumberProperty('maxProgressionStep', 1)
        self._addNumberProperty('finishedLevelsCount', 0)
        self._addNumberProperty('nextTimeEnable', 0)
        self._addStringProperty('state')
        self.onClick = self._addCommand('onClick')
