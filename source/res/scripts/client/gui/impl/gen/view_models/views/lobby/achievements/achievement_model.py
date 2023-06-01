# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/achievement_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class AchievementType(Enum):
    REPEATABLE = 'repeatable'
    CLASS = 'class'
    CUSTOM = 'custom'
    SERIES = 'series'
    SINGLE = 'single'
    RARE = 'rare'


class CounterType(Enum):
    NONE = 'none'
    SIMPLE = 'simple'
    SERIES = 'series'
    STAGES = 'stages'


class AchievementModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(AchievementModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getResourceName(self):
        return self._getString(1)

    def setResourceName(self, value):
        self._setString(1, value)

    def getBlock(self):
        return self._getString(2)

    def setBlock(self, value):
        self._setString(2, value)

    def getType(self):
        return AchievementType(self._getString(3))

    def setType(self, value):
        self._setString(3, value.value)

    def getCounterType(self):
        return CounterType(self._getString(4))

    def setCounterType(self, value):
        self._setString(4, value.value)

    def getValue(self):
        return self._getNumber(5)

    def setValue(self, value):
        self._setNumber(5, value)

    def getRareIconId(self):
        return self._getString(6)

    def setRareIconId(self, value):
        self._setString(6, value)

    def getRareBigIconId(self):
        return self._getString(7)

    def setRareBigIconId(self, value):
        self._setString(7, value)

    def getIsNew(self):
        return self._getBool(8)

    def setIsNew(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(AchievementModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('resourceName', '')
        self._addStringProperty('block', '')
        self._addStringProperty('type')
        self._addStringProperty('counterType')
        self._addNumberProperty('value', 0)
        self._addStringProperty('rareIconId', '')
        self._addStringProperty('rareBigIconId', '')
        self._addBoolProperty('isNew', False)
