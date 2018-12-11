# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_bonus_tooltip_model.py
from frameworks.wulf import ViewModel

class NewYearBonusTooltipModel(ViewModel):
    __slots__ = ()

    def getCredits(self):
        return self._getNumber(0)

    def setCredits(self, value):
        self._setNumber(0, value)

    def getXp(self):
        return self._getNumber(1)

    def setXp(self, value):
        self._setNumber(1, value)

    def getFree_xp(self):
        return self._getNumber(2)

    def setFree_xp(self, value):
        self._setNumber(2, value)

    def getCrew_xp(self):
        return self._getNumber(3)

    def setCrew_xp(self, value):
        self._setNumber(3, value)

    def getIsMaxLevel(self):
        return self._getBool(4)

    def setIsMaxLevel(self, value):
        self._setBool(4, value)

    def getIsFullCollection(self):
        return self._getBool(5)

    def setIsFullCollection(self, value):
        self._setBool(5, value)

    def getDate(self):
        return self._getString(6)

    def setDate(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(NewYearBonusTooltipModel, self)._initialize()
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('xp', 0)
        self._addNumberProperty('free_xp', 0)
        self._addNumberProperty('crew_xp', 0)
        self._addBoolProperty('isMaxLevel', False)
        self._addBoolProperty('isFullCollection', False)
        self._addStringProperty('date', '')
