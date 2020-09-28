# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_lootbox_open_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.stats_model import StatsModel
from gui.impl.gen.view_models.views.lobby.wt_event.reward_item_model import RewardItemModel

class WtEventLootboxOpenViewModel(ViewModel):
    __slots__ = ('openBox', 'showRerollRewardOverlay', 'runPickRewardAnimation', 'pickReward', 'goToStorage', 'goToBuySpecial', 'videoReady', 'close', 'onShowRewards')

    def __init__(self, properties=16, commands=9):
        super(WtEventLootboxOpenViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardData(self):
        return self._getViewModel(0)

    @property
    def stats(self):
        return self._getViewModel(1)

    def getIsActive(self):
        return self._getBool(2)

    def setIsActive(self, value):
        self._setBool(2, value)

    def getBoxType(self):
        return self._getString(3)

    def setBoxType(self, value):
        self._setString(3, value)

    def getBoxCount(self):
        return self._getNumber(4)

    def setBoxCount(self, value):
        self._setNumber(4, value)

    def getCurrentBoxCount(self):
        return self._getNumber(5)

    def setCurrentBoxCount(self, value):
        self._setNumber(5, value)

    def getRerollPrice(self):
        return self._getNumber(6)

    def setRerollPrice(self, value):
        self._setNumber(6, value)

    def getRerollCurrency(self):
        return self._getString(7)

    def setRerollCurrency(self, value):
        self._setString(7, value)

    def getRerollAttempts(self):
        return self._getNumber(8)

    def setRerollAttempts(self, value):
        self._setNumber(8, value)

    def getAccrued(self):
        return self._getNumber(9)

    def setAccrued(self, value):
        self._setNumber(9, value)

    def getShowAccrued(self):
        return self._getBool(10)

    def setShowAccrued(self, value):
        self._setBool(10, value)

    def getAnimationType(self):
        return self._getString(11)

    def setAnimationType(self, value):
        self._setString(11, value)

    def getBoxState(self):
        return self._getString(12)

    def setBoxState(self, value):
        self._setString(12, value)

    def getHasChildOverlay(self):
        return self._getBool(13)

    def setHasChildOverlay(self, value):
        self._setBool(13, value)

    def getRewardDataInvalidator(self):
        return self._getNumber(14)

    def setRewardDataInvalidator(self, value):
        self._setNumber(14, value)

    def getIsOpenedAfterInitialLoad(self):
        return self._getBool(15)

    def setIsOpenedAfterInitialLoad(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(WtEventLootboxOpenViewModel, self)._initialize()
        self._addViewModelProperty('rewardData', UserListModel())
        self._addViewModelProperty('stats', StatsModel())
        self._addBoolProperty('isActive', True)
        self._addStringProperty('boxType', 'special')
        self._addNumberProperty('boxCount', 0)
        self._addNumberProperty('currentBoxCount', 0)
        self._addNumberProperty('rerollPrice', 25000)
        self._addStringProperty('rerollCurrency', 'credits')
        self._addNumberProperty('rerollAttempts', 3)
        self._addNumberProperty('accrued', 0)
        self._addBoolProperty('showAccrued', False)
        self._addStringProperty('animationType', 'default')
        self._addStringProperty('boxState', 'closed')
        self._addBoolProperty('hasChildOverlay', False)
        self._addNumberProperty('rewardDataInvalidator', 1)
        self._addBoolProperty('isOpenedAfterInitialLoad', False)
        self.openBox = self._addCommand('openBox')
        self.showRerollRewardOverlay = self._addCommand('showRerollRewardOverlay')
        self.runPickRewardAnimation = self._addCommand('runPickRewardAnimation')
        self.pickReward = self._addCommand('pickReward')
        self.goToStorage = self._addCommand('goToStorage')
        self.goToBuySpecial = self._addCommand('goToBuySpecial')
        self.videoReady = self._addCommand('videoReady')
        self.close = self._addCommand('close')
        self.onShowRewards = self._addCommand('onShowRewards')
