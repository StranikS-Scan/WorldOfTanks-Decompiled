# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/loot_box_reward_window_content_model.py
import typing
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.button_model import ButtonModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class LootBoxRewardWindowContentModel(ViewModel):
    __slots__ = ('onConfirmBtnClicked',)

    @property
    def confirmBtn(self):
        return self._getViewModel(0)

    @property
    def rewardsList(self):
        return self._getViewModel(1)

    def getEventName(self):
        return self._getString(2)

    def setEventName(self, value):
        self._setString(2, value)

    def getShowRewards(self):
        return self._getBool(3)

    def setShowRewards(self, value):
        self._setBool(3, value)

    def getRewardsCount(self):
        return self._getNumber(4)

    def setRewardsCount(self, value):
        self._setNumber(4, value)

    def getLootboxType(self):
        return self._getString(5)

    def setLootboxType(self, value):
        self._setString(5, value)

    def getIsFree(self):
        return self._getBool(6)

    def setIsFree(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(LootBoxRewardWindowContentModel, self)._initialize()
        self._addViewModelProperty('confirmBtn', ButtonModel())
        self._addViewModelProperty('rewardsList', ListModel())
        self._addStringProperty('eventName', '')
        self._addBoolProperty('showRewards', False)
        self._addNumberProperty('rewardsCount', 0)
        self._addStringProperty('lootboxType', '')
        self._addBoolProperty('isFree', False)
        self.onConfirmBtnClicked = self._addCommand('onConfirmBtnClicked')
