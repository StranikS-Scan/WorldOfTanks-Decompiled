# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dragon_boat/final_rewards_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.dragon_boat.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.dragon_boat.reward_item_model import RewardItemModel

class RewardReason(Enum):
    STYLE_UPGRADE = 'styleUpgradeReason'
    DEFAULT = 'defaultReason'


class FinalRewardsViewModel(CommonViewModel):
    __slots__ = ('onBuyClick',)

    def __init__(self, properties=13, commands=2):
        super(FinalRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(4)

    @property
    def additionalRewards(self):
        return self._getViewModel(5)

    def getChapterID(self):
        return self._getNumber(6)

    def setChapterID(self, value):
        self._setNumber(6, value)

    def getReason(self):
        return RewardReason(self._getString(7))

    def setReason(self, value):
        self._setString(7, value.value)

    def getIsFinalReward(self):
        return self._getBool(8)

    def setIsFinalReward(self, value):
        self._setBool(8, value)

    def getIsBaseStyleLevel(self):
        return self._getBool(9)

    def setIsBaseStyleLevel(self, value):
        self._setBool(9, value)

    def getIsNeedToShowOffer(self):
        return self._getBool(10)

    def setIsNeedToShowOffer(self, value):
        self._setBool(10, value)

    def getSeasonStopped(self):
        return self._getBool(11)

    def setSeasonStopped(self, value):
        self._setBool(11, value)

    def getWideRewardsIDs(self):
        return self._getArray(12)

    def setWideRewardsIDs(self, value):
        self._setArray(12, value)

    def _initialize(self):
        super(FinalRewardsViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('reason')
        self._addBoolProperty('isFinalReward', False)
        self._addBoolProperty('isBaseStyleLevel', False)
        self._addBoolProperty('isNeedToShowOffer', False)
        self._addBoolProperty('seasonStopped', False)
        self._addArrayProperty('wideRewardsIDs', Array())
        self.onBuyClick = self._addCommand('onBuyClick')
