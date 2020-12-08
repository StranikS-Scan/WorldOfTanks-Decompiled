# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_premium_multi_open_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_multi_open_renderer_model import LootBoxMultiOpenRendererModel

class LootBoxPremiumMultiOpenViewModel(ViewModel):
    __slots__ = ('onOpenBox', 'showSpecialReward', 'onContinueOpening', 'onPauseOpening', 'openNextBoxes', 'onCloseBtnClick', 'onViewShowed')
    WINDOW_MAX_BOX_COUNT = 5

    def __init__(self, properties=14, commands=7):
        super(LootBoxPremiumMultiOpenViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    def getRewardSize(self):
        return self._getString(1)

    def setRewardSize(self, value):
        self._setString(1, value)

    def getBoxesCounter(self):
        return self._getNumber(2)

    def setBoxesCounter(self, value):
        self._setNumber(2, value)

    def getLimitToOpen(self):
        return self._getNumber(3)

    def setLimitToOpen(self, value):
        self._setNumber(3, value)

    def getBoxCategory(self):
        return self._getString(4)

    def setBoxCategory(self, value):
        self._setString(4, value)

    def getIsLootboxesEnabled(self):
        return self._getBool(5)

    def setIsLootboxesEnabled(self, value):
        self._setBool(5, value)

    def getHardReset(self):
        return self._getBool(6)

    def setHardReset(self, value):
        self._setBool(6, value)

    def getIsPausedForSpecial(self):
        return self._getBool(7)

    def setIsPausedForSpecial(self, value):
        self._setBool(7, value)

    def getIsOnPause(self):
        return self._getBool(8)

    def setIsOnPause(self, value):
        self._setBool(8, value)

    def getLeftToOpenCount(self):
        return self._getNumber(9)

    def setLeftToOpenCount(self, value):
        self._setNumber(9, value)

    def getCurrentPage(self):
        return self._getNumber(10)

    def setCurrentPage(self, value):
        self._setNumber(10, value)

    def getIsServerError(self):
        return self._getBool(11)

    def setIsServerError(self, value):
        self._setBool(11, value)

    def getNeedToOpen(self):
        return self._getNumber(12)

    def setNeedToOpen(self, value):
        self._setNumber(12, value)

    def getIsMemoryRiskySystem(self):
        return self._getBool(13)

    def setIsMemoryRiskySystem(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(LootBoxPremiumMultiOpenViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('rewardSize', '')
        self._addNumberProperty('boxesCounter', 0)
        self._addNumberProperty('limitToOpen', 0)
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('isLootboxesEnabled', True)
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('isPausedForSpecial', False)
        self._addBoolProperty('isOnPause', False)
        self._addNumberProperty('leftToOpenCount', 0)
        self._addNumberProperty('currentPage', 0)
        self._addBoolProperty('isServerError', False)
        self._addNumberProperty('needToOpen', 0)
        self._addBoolProperty('isMemoryRiskySystem', False)
        self.onOpenBox = self._addCommand('onOpenBox')
        self.showSpecialReward = self._addCommand('showSpecialReward')
        self.onContinueOpening = self._addCommand('onContinueOpening')
        self.onPauseOpening = self._addCommand('onPauseOpening')
        self.openNextBoxes = self._addCommand('openNextBoxes')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onViewShowed = self._addCommand('onViewShowed')
