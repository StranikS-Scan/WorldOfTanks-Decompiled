# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/bunks_confirm_discount_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BunksConfirmDiscountTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BunksConfirmDiscountTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getBunksCount(self):
        return self._getNumber(0)

    def setBunksCount(self, value):
        self._setNumber(0, value)

    def getOldCost(self):
        return self._getNumber(1)

    def setOldCost(self, value):
        self._setNumber(1, value)

    def getNewCost(self):
        return self._getNumber(2)

    def setNewCost(self, value):
        self._setNumber(2, value)

    def getIsEnough(self):
        return self._getBool(3)

    def setIsEnough(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BunksConfirmDiscountTooltipViewModel, self)._initialize()
        self._addNumberProperty('bunksCount', 1)
        self._addNumberProperty('oldCost', 1)
        self._addNumberProperty('newCost', 1)
        self._addBoolProperty('isEnough', False)
