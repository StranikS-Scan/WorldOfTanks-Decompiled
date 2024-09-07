# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_awards_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class RewardReason(Enum):
    BUY_BATTLE_PASS = 'buyBattlePassReason'
    BUY_BATTLE_PASS_LEVELS = 'buyBattlePassLevelsReason'
    BUY_MULTIPLE_BATTLE_PASS = 'buyMultipleBattlePassReason'
    STYLE_UPGRADE = 'styleUpgradeReason'
    DEFAULT = 'defaultReason'
    GIFT_CHAPTER = 'giftChapterReason'


class ChapterType(Enum):
    DEFAULT = 'default'
    MARATHON = 'marathon'
    RESOURCE = 'resource'


class BattlePassAwardsViewModel(CommonViewModel):
    __slots__ = ('onBuyClick',)

    def __init__(self, properties=16, commands=2):
        super(BattlePassAwardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(4)

    @staticmethod
    def getMainRewardsType():
        return RewardItemModel

    @property
    def additionalRewards(self):
        return self._getViewModel(5)

    @staticmethod
    def getAdditionalRewardsType():
        return RewardItemModel

    @property
    def packageRewards(self):
        return self._getViewModel(6)

    @staticmethod
    def getPackageRewardsType():
        return RewardItemModel

    def getChapterID(self):
        return self._getNumber(7)

    def setChapterID(self, value):
        self._setNumber(7, value)

    def getReason(self):
        return RewardReason(self._getString(8))

    def setReason(self, value):
        self._setString(8, value.value)

    def getIsFinalReward(self):
        return self._getBool(9)

    def setIsFinalReward(self, value):
        self._setBool(9, value)

    def getIsBaseStyleLevel(self):
        return self._getBool(10)

    def setIsBaseStyleLevel(self, value):
        self._setBool(10, value)

    def getIsNeedToShowOffer(self):
        return self._getBool(11)

    def setIsNeedToShowOffer(self, value):
        self._setBool(11, value)

    def getSeasonStopped(self):
        return self._getBool(12)

    def setSeasonStopped(self, value):
        self._setBool(12, value)

    def getWideRewardsIDs(self):
        return self._getArray(13)

    def setWideRewardsIDs(self, value):
        self._setArray(13, value)

    @staticmethod
    def getWideRewardsIDsType():
        return int

    def getChapterType(self):
        return ChapterType(self._getString(14))

    def setChapterType(self, value):
        self._setString(14, value.value)

    def getAvailableChapterTypes(self):
        return self._getArray(15)

    def setAvailableChapterTypes(self, value):
        self._setArray(15, value)

    @staticmethod
    def getAvailableChapterTypesType():
        return unicode

    def _initialize(self):
        super(BattlePassAwardsViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addViewModelProperty('packageRewards', UserListModel())
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('reason')
        self._addBoolProperty('isFinalReward', False)
        self._addBoolProperty('isBaseStyleLevel', False)
        self._addBoolProperty('isNeedToShowOffer', False)
        self._addBoolProperty('seasonStopped', False)
        self._addArrayProperty('wideRewardsIDs', Array())
        self._addStringProperty('chapterType')
        self._addArrayProperty('availableChapterTypes', Array())
        self.onBuyClick = self._addCommand('onBuyClick')
