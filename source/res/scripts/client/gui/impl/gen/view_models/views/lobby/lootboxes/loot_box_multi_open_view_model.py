# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_multi_open_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_common_open_view_model import LootBoxCommonOpenViewModel

class LootBoxMultiOpenViewModel(LootBoxCommonOpenViewModel):
    __slots__ = ('onOpenBox', 'onReadyToRestart', 'showSpecialReward', 'onContinueOpening', 'onPauseOpening')

    def __init__(self, properties=18, commands=6):
        super(LootBoxMultiOpenViewModel, self).__init__(properties=properties, commands=commands)

    def getOpenedCount(self):
        return self._getNumber(2)

    def setOpenedCount(self, value):
        self._setNumber(2, value)

    def getBoxesCounter(self):
        return self._getNumber(3)

    def setBoxesCounter(self, value):
        self._setNumber(3, value)

    def getLimitToOpen(self):
        return self._getNumber(4)

    def setLimitToOpen(self, value):
        self._setNumber(4, value)

    def getLootboxType(self):
        return self._getString(5)

    def setLootboxType(self, value):
        self._setString(5, value)

    def getLootboxIcon(self):
        return self._getResource(6)

    def setLootboxIcon(self, value):
        self._setResource(6, value)

    def getBoxCategory(self):
        return self._getString(7)

    def setBoxCategory(self, value):
        self._setString(7, value)

    def getRestart(self):
        return self._getBool(8)

    def setRestart(self, value):
        self._setBool(8, value)

    def getIsFreeBox(self):
        return self._getBool(9)

    def setIsFreeBox(self, value):
        self._setBool(9, value)

    def getIsLootboxesEnabled(self):
        return self._getBool(10)

    def setIsLootboxesEnabled(self, value):
        self._setBool(10, value)

    def getHardReset(self):
        return self._getBool(11)

    def setHardReset(self, value):
        self._setBool(11, value)

    def getIsPausedForSpecial(self):
        return self._getBool(12)

    def setIsPausedForSpecial(self, value):
        self._setBool(12, value)

    def getIsOnPause(self):
        return self._getBool(13)

    def setIsOnPause(self, value):
        self._setBool(13, value)

    def getStartShowIndex(self):
        return self._getNumber(14)

    def setStartShowIndex(self, value):
        self._setNumber(14, value)

    def getLeftToOpenCount(self):
        return self._getNumber(15)

    def setLeftToOpenCount(self, value):
        self._setNumber(15, value)

    def getCurrentPage(self):
        return self._getNumber(16)

    def setCurrentPage(self, value):
        self._setNumber(16, value)

    def getIsServerError(self):
        return self._getBool(17)

    def setIsServerError(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(LootBoxMultiOpenViewModel, self)._initialize()
        self._addNumberProperty('openedCount', 0)
        self._addNumberProperty('boxesCounter', 0)
        self._addNumberProperty('limitToOpen', 0)
        self._addStringProperty('lootboxType', '')
        self._addResourceProperty('lootboxIcon', R.invalid())
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('restart', False)
        self._addBoolProperty('isFreeBox', False)
        self._addBoolProperty('isLootboxesEnabled', True)
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('isPausedForSpecial', False)
        self._addBoolProperty('isOnPause', False)
        self._addNumberProperty('startShowIndex', 0)
        self._addNumberProperty('leftToOpenCount', 0)
        self._addNumberProperty('currentPage', 0)
        self._addBoolProperty('isServerError', False)
        self.onOpenBox = self._addCommand('onOpenBox')
        self.onReadyToRestart = self._addCommand('onReadyToRestart')
        self.showSpecialReward = self._addCommand('showSpecialReward')
        self.onContinueOpening = self._addCommand('onContinueOpening')
        self.onPauseOpening = self._addCommand('onPauseOpening')
