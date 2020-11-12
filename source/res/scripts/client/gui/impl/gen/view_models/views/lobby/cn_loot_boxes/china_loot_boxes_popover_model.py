# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/cn_loot_boxes/china_loot_boxes_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ChinaLootBoxesPopoverModel(ViewModel):
    __slots__ = ('onOpenBtnClick', 'onBuyBtnClick', 'onAboutBtnClick')

    def __init__(self, properties=7, commands=3):
        super(ChinaLootBoxesPopoverModel, self).__init__(properties=properties, commands=commands)

    def getEntryList(self):
        return self._getArray(0)

    def setEntryList(self, value):
        self._setArray(0, value)

    def getIsDisabled(self):
        return self._getBool(1)

    def setIsDisabled(self, value):
        self._setBool(1, value)

    def getMaxBoxesAvailableToBuy(self):
        return self._getNumber(2)

    def setMaxBoxesAvailableToBuy(self, value):
        self._setNumber(2, value)

    def getBoxesAvailableToBuy(self):
        return self._getNumber(3)

    def setBoxesAvailableToBuy(self, value):
        self._setNumber(3, value)

    def getIsLastEventDay(self):
        return self._getBool(4)

    def setIsLastEventDay(self, value):
        self._setBool(4, value)

    def getBuyingEnableMinutes(self):
        return self._getNumber(5)

    def setBuyingEnableMinutes(self, value):
        self._setNumber(5, value)

    def getIsEntitlementCacheInited(self):
        return self._getBool(6)

    def setIsEntitlementCacheInited(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(ChinaLootBoxesPopoverModel, self)._initialize()
        self._addArrayProperty('entryList', Array())
        self._addBoolProperty('isDisabled', False)
        self._addNumberProperty('maxBoxesAvailableToBuy', 0)
        self._addNumberProperty('boxesAvailableToBuy', 0)
        self._addBoolProperty('isLastEventDay', False)
        self._addNumberProperty('buyingEnableMinutes', 0)
        self._addBoolProperty('isEntitlementCacheInited', True)
        self.onOpenBtnClick = self._addCommand('onOpenBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onAboutBtnClick = self._addCommand('onAboutBtnClick')
