# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/loot_box_multi_open_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_reward_row_model import LootBoxRewardRowModel

class LootBoxMultiOpenViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onShowAnimationBtnClick', 'showSpecialReward', 'onOpenBox', 'onReadyToRestart', 'onContinueOpening', 'onPauseOpening')
    USUAL_BOX_TYPE = 'newYear_usual'
    PREMIUM_BOX_TYPE = 'newYear_premium'

    def __init__(self, properties=18, commands=7):
        super(LootBoxMultiOpenViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardRows(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardRowsType():
        return LootBoxRewardRowModel

    def getOpenedCount(self):
        return self._getNumber(1)

    def setOpenedCount(self, value):
        self._setNumber(1, value)

    def getBoxesCounter(self):
        return self._getNumber(2)

    def setBoxesCounter(self, value):
        self._setNumber(2, value)

    def getLimitToOpen(self):
        return self._getNumber(3)

    def setLimitToOpen(self, value):
        self._setNumber(3, value)

    def getLootboxType(self):
        return self._getString(4)

    def setLootboxType(self, value):
        self._setString(4, value)

    def getLootboxIcon(self):
        return self._getResource(5)

    def setLootboxIcon(self, value):
        self._setResource(5, value)

    def getBoxCategory(self):
        return self._getString(6)

    def setBoxCategory(self, value):
        self._setString(6, value)

    def getRestart(self):
        return self._getBool(7)

    def setRestart(self, value):
        self._setBool(7, value)

    def getIsFreeBox(self):
        return self._getBool(8)

    def setIsFreeBox(self, value):
        self._setBool(8, value)

    def getIsLootboxesEnabled(self):
        return self._getBool(9)

    def setIsLootboxesEnabled(self, value):
        self._setBool(9, value)

    def getHardReset(self):
        return self._getBool(10)

    def setHardReset(self, value):
        self._setBool(10, value)

    def getIsPausedForSpecial(self):
        return self._getBool(11)

    def setIsPausedForSpecial(self, value):
        self._setBool(11, value)

    def getIsOnPause(self):
        return self._getBool(12)

    def setIsOnPause(self, value):
        self._setBool(12, value)

    def getStartShowIndex(self):
        return self._getNumber(13)

    def setStartShowIndex(self, value):
        self._setNumber(13, value)

    def getLeftToOpenCount(self):
        return self._getNumber(14)

    def setLeftToOpenCount(self, value):
        self._setNumber(14, value)

    def getCurrentPage(self):
        return self._getNumber(15)

    def setCurrentPage(self, value):
        self._setNumber(15, value)

    def getIsServerError(self):
        return self._getBool(16)

    def setIsServerError(self, value):
        self._setBool(16, value)

    def getIsAnimationEnabled(self):
        return self._getBool(17)

    def setIsAnimationEnabled(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(LootBoxMultiOpenViewModel, self)._initialize()
        self._addViewModelProperty('rewardRows', UserListModel())
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
        self._addBoolProperty('isAnimationEnabled', False)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onShowAnimationBtnClick = self._addCommand('onShowAnimationBtnClick')
        self.showSpecialReward = self._addCommand('showSpecialReward')
        self.onOpenBox = self._addCommand('onOpenBox')
        self.onReadyToRestart = self._addCommand('onReadyToRestart')
        self.onContinueOpening = self._addCommand('onContinueOpening')
        self.onPauseOpening = self._addCommand('onPauseOpening')
