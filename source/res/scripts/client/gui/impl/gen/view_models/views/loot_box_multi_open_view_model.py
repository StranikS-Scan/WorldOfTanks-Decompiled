# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_multi_open_view_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class LootBoxMultiOpenViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onOpenBoxBtnClick', 'onReadyToRestart', 'showSpecialReward')

    def getOpenedCount(self):
        return self._getNumber(0)

    def setOpenedCount(self, value):
        self._setNumber(0, value)

    def getBoxesCounter(self):
        return self._getNumber(1)

    def setBoxesCounter(self, value):
        self._setNumber(1, value)

    def getLimitToOpen(self):
        return self._getNumber(2)

    def setLimitToOpen(self, value):
        self._setNumber(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    def getLootboxType(self):
        return self._getString(4)

    def setLootboxType(self, value):
        self._setString(4, value)

    def getBoxCategory(self):
        return self._getString(5)

    def setBoxCategory(self, value):
        self._setString(5, value)

    def getRestart(self):
        return self._getBool(6)

    def setRestart(self, value):
        self._setBool(6, value)

    def getIsFreeBox(self):
        return self._getBool(7)

    def setIsFreeBox(self, value):
        self._setBool(7, value)

    def getIsOpenBoxBtnEnabled(self):
        return self._getBool(8)

    def setIsOpenBoxBtnEnabled(self, value):
        self._setBool(8, value)

    def getHardReset(self):
        return self._getBool(9)

    def setHardReset(self, value):
        self._setBool(9, value)

    def getIsCanNext(self):
        return self._getBool(10)

    def setIsCanNext(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(LootBoxMultiOpenViewModel, self)._initialize()
        self._addNumberProperty('openedCount', 0)
        self._addNumberProperty('boxesCounter', 0)
        self._addNumberProperty('limitToOpen', 0)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('lootboxType', '')
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('restart', False)
        self._addBoolProperty('isFreeBox', False)
        self._addBoolProperty('isOpenBoxBtnEnabled', True)
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('isCanNext', True)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onOpenBoxBtnClick = self._addCommand('onOpenBoxBtnClick')
        self.onReadyToRestart = self._addCommand('onReadyToRestart')
        self.showSpecialReward = self._addCommand('showSpecialReward')
