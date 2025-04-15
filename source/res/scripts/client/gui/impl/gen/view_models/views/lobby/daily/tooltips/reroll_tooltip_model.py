# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/tooltips/reroll_tooltip_model.py
from frameworks.wulf import ViewModel

class RerollTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(RerollTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCanReroll(self):
        return self._getBool(0)

    def setCanReroll(self, value):
        self._setBool(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getIsBonusCompleted(self):
        return self._getBool(2)

    def setIsBonusCompleted(self, value):
        self._setBool(2, value)

    def getIsPremium(self):
        return self._getBool(3)

    def setIsPremium(self, value):
        self._setBool(3, value)

    def getIsPremiumActive(self):
        return self._getBool(4)

    def setIsPremiumActive(self, value):
        self._setBool(4, value)

    def getTimeToUpdate(self):
        return self._getNumber(5)

    def setTimeToUpdate(self, value):
        self._setNumber(5, value)

    def getRerollCooldown(self):
        return self._getNumber(6)

    def setRerollCooldown(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(RerollTooltipModel, self)._initialize()
        self._addBoolProperty('canReroll', False)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isBonusCompleted', False)
        self._addBoolProperty('isPremium', False)
        self._addBoolProperty('isPremiumActive', False)
        self._addNumberProperty('timeToUpdate', 0)
        self._addNumberProperty('rerollCooldown', 0)
