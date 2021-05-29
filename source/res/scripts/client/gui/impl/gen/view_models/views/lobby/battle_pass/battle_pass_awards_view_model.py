# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_awards_view_model.py
from frameworks.wulf import Array
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class BattlePassAwardsViewModel(CommonViewModel):
    __slots__ = ('onBuyClick', 'onStyleSelectClick')
    BUY_BATTLE_PASS_REASON = 'buyBattlePassReason'
    BUY_BATTLE_PASS_LEVELS_REASON = 'buyBattlePassLevelsReason'
    BUY_MULTIPLE_BATTLE_PASS_REASON = 'buyMultipleBattlePassReason'
    SELECT_TROPHY_DEVICE_REASON = 'selectTrophyDeviceReason'
    SELECT_STYLE_REASON = 'selectStyleReason'
    DEFAULT_REASON = 'defaultReason'

    def __init__(self, properties=16, commands=3):
        super(BattlePassAwardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(4)

    @property
    def additionalRewards(self):
        return self._getViewModel(5)

    def getPreviousLevel(self):
        return self._getNumber(6)

    def setPreviousLevel(self, value):
        self._setNumber(6, value)

    def getChapter(self):
        return self._getString(7)

    def setChapter(self, value):
        self._setString(7, value)

    def getChapterNumber(self):
        return self._getNumber(8)

    def setChapterNumber(self, value):
        self._setNumber(8, value)

    def getReason(self):
        return self._getString(9)

    def setReason(self, value):
        self._setString(9, value)

    def getIsFinalReward(self):
        return self._getBool(10)

    def setIsFinalReward(self, value):
        self._setBool(10, value)

    def getIsNeedToShowOffer(self):
        return self._getBool(11)

    def setIsNeedToShowOffer(self, value):
        self._setBool(11, value)

    def getIsStyleChosen(self):
        return self._getBool(12)

    def setIsStyleChosen(self, value):
        self._setBool(12, value)

    def getIsBaseLevelStyle(self):
        return self._getBool(13)

    def setIsBaseLevelStyle(self, value):
        self._setBool(13, value)

    def getSeasonStopped(self):
        return self._getBool(14)

    def setSeasonStopped(self, value):
        self._setBool(14, value)

    def getWideRewardsIDs(self):
        return self._getArray(15)

    def setWideRewardsIDs(self, value):
        self._setArray(15, value)

    def _initialize(self):
        super(BattlePassAwardsViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addNumberProperty('previousLevel', 0)
        self._addStringProperty('chapter', '')
        self._addNumberProperty('chapterNumber', 0)
        self._addStringProperty('reason', 'defaultReason')
        self._addBoolProperty('isFinalReward', False)
        self._addBoolProperty('isNeedToShowOffer', False)
        self._addBoolProperty('isStyleChosen', False)
        self._addBoolProperty('isBaseLevelStyle', False)
        self._addBoolProperty('seasonStopped', False)
        self._addArrayProperty('wideRewardsIDs', Array())
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onStyleSelectClick = self._addCommand('onStyleSelectClick')
