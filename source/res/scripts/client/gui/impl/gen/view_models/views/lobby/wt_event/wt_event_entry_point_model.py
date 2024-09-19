# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_entry_point_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    BEFORE = 0
    ACTIVE = 1
    NOTPRIMETIME = 2
    AFTER = 3


class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class WtEventEntryPointModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=9, commands=1):
        super(WtEventEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getLeftTime(self):
        return self._getNumber(1)

    def setLeftTime(self, value):
        self._setNumber(1, value)

    def getEndTime(self):
        return self._getNumber(2)

    def setEndTime(self, value):
        self._setNumber(2, value)

    def getStartTime(self):
        return self._getNumber(3)

    def setStartTime(self, value):
        self._setNumber(3, value)

    def getHunterLootBoxesCount(self):
        return self._getNumber(4)

    def setHunterLootBoxesCount(self, value):
        self._setNumber(4, value)

    def getBossLootBoxesCount(self):
        return self._getNumber(5)

    def setBossLootBoxesCount(self, value):
        self._setNumber(5, value)

    def getIsNew(self):
        return self._getBool(6)

    def setIsNew(self, value):
        self._setBool(6, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(7))

    def setPerformanceRisk(self, value):
        self._setString(7, value.value)

    def getIsSingle(self):
        return self._getBool(8)

    def setIsSingle(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(WtEventEntryPointModel, self)._initialize()
        self._addNumberProperty('state')
        self._addNumberProperty('leftTime', -1)
        self._addNumberProperty('endTime', -1)
        self._addNumberProperty('startTime', -1)
        self._addNumberProperty('hunterLootBoxesCount', 0)
        self._addNumberProperty('bossLootBoxesCount', 0)
        self._addBoolProperty('isNew', False)
        self._addStringProperty('performanceRisk')
        self._addBoolProperty('isSingle', False)
        self.onClick = self._addCommand('onClick')
