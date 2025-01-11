# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/lobby/banner_entry_point/grinch_banner_entry_point_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    STARTSOON = 'startSoon'
    ACTIVE = 'active'
    DISABLED = 'disabled'
    ENDSOON = 'endSoon'
    PAUSE = 'pause'
    POSTMORTEM = 'postmortem'


class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class GrinchBannerEntryPointModel(ViewModel):
    __slots__ = ('onOpen',)

    def __init__(self, properties=7, commands=1):
        super(GrinchBannerEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getIsSingle(self):
        return self._getBool(1)

    def setIsSingle(self, value):
        self._setBool(1, value)

    def getTimestamp(self):
        return self._getNumber(2)

    def setTimestamp(self, value):
        self._setNumber(2, value)

    def getEndTimestamp(self):
        return self._getNumber(3)

    def setEndTimestamp(self, value):
        self._setNumber(3, value)

    def getIsNew(self):
        return self._getBool(4)

    def setIsNew(self, value):
        self._setBool(4, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(5))

    def setPerformanceRisk(self, value):
        self._setString(5, value.value)

    def getChapter(self):
        return self._getNumber(6)

    def setChapter(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(GrinchBannerEntryPointModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('isSingle', False)
        self._addNumberProperty('timestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addBoolProperty('isNew', False)
        self._addStringProperty('performanceRisk')
        self._addNumberProperty('chapter', 0)
        self.onOpen = self._addCommand('onOpen')
