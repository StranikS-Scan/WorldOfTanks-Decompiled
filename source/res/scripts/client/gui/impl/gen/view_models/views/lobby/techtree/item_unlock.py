# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/item_unlock.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class ItemUnlock(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ItemUnlock, self).__init__(properties=properties, commands=commands)

    @property
    def xpCost(self):
        return self._getViewModel(0)

    @staticmethod
    def getXpCostType():
        return PriceModel

    def getParentID(self):
        return self._getNumber(1)

    def setParentID(self, value):
        self._setNumber(1, value)

    def getUnlockIdx(self):
        return self._getNumber(2)

    def setUnlockIdx(self, value):
        self._setNumber(2, value)

    def getRequiredItems(self):
        return self._getArray(3)

    def setRequiredItems(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRequiredItemsType():
        return int

    def _initialize(self):
        super(ItemUnlock, self)._initialize()
        self._addViewModelProperty('xpCost', PriceModel())
        self._addNumberProperty('parentID', 0)
        self._addNumberProperty('unlockIdx', 0)
        self._addArrayProperty('requiredItems', Array())
