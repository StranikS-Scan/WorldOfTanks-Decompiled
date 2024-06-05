# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/advanced_achievement_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class AdvancedAchievementType(Enum):
    SINGLE = 'single'
    CUMULATIVE = 'cumulative'
    STAGED = 'staged'
    SUBCATEGORY = 'subcategory'
    CATEGORY = 'Category'


class AdvancedAchievementIconPosition(Enum):
    TOP = 'top'
    CENTER = 'center'
    BOTTOM = 'bottom'


class AdvancedAchievementIconSizeMap(Enum):
    DEFAULT = ''
    PERSONALMISSIONS = 'personal_missions'


class AdvancedAchievementModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(AdvancedAchievementModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return AdvancedAchievementType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getKey(self):
        return self._getString(1)

    def setKey(self, value):
        self._setString(1, value)

    def getCategory(self):
        return self._getString(2)

    def setCategory(self, value):
        self._setString(2, value)

    def getId(self):
        return self._getNumber(3)

    def setId(self, value):
        self._setNumber(3, value)

    def getBackground(self):
        return self._getString(4)

    def setBackground(self, value):
        self._setString(4, value)

    def getTheme(self):
        return self._getString(5)

    def setTheme(self, value):
        self._setString(5, value)

    def getIconPosition(self):
        return AdvancedAchievementIconPosition(self._getString(6))

    def setIconPosition(self, value):
        self._setString(6, value.value)

    def getIconSizeMap(self):
        return AdvancedAchievementIconSizeMap(self._getString(7))

    def setIconSizeMap(self, value):
        self._setString(7, value.value)

    def getCurrentValue(self):
        return self._getNumber(8)

    def setCurrentValue(self, value):
        self._setNumber(8, value)

    def getMaxValue(self):
        return self._getNumber(9)

    def setMaxValue(self, value):
        self._setNumber(9, value)

    def getAchievementScore(self):
        return self._getNumber(10)

    def setAchievementScore(self, value):
        self._setNumber(10, value)

    def getStage(self):
        return self._getNumber(11)

    def setStage(self, value):
        self._setNumber(11, value)

    def getIsTrophy(self):
        return self._getBool(12)

    def setIsTrophy(self, value):
        self._setBool(12, value)

    def getReceivedDate(self):
        return self._getString(13)

    def setReceivedDate(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(AdvancedAchievementModel, self)._initialize()
        self._addStringProperty('type')
        self._addStringProperty('key', '')
        self._addStringProperty('category', '')
        self._addNumberProperty('id', 0)
        self._addStringProperty('background', '')
        self._addStringProperty('theme', '')
        self._addStringProperty('iconPosition')
        self._addStringProperty('iconSizeMap')
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('achievementScore', 0)
        self._addNumberProperty('stage', 0)
        self._addBoolProperty('isTrophy', False)
        self._addStringProperty('receivedDate', '')
