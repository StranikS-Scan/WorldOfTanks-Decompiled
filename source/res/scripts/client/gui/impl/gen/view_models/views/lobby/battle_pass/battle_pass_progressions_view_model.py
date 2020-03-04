# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_progressions_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel

class BattlePassProgressionsViewModel(CommonViewModel):
    __slots__ = ('onClose', 'onAboutClick', 'onInfoBtnClick', 'onBuyClick', 'onBuyBtnClick', 'onExtrasClick', 'onVotingResultClick', 'onViewLoaded')

    def __init__(self, properties=31, commands=9):
        super(BattlePassProgressionsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def intro(self):
        return self._getViewModel(7)

    @property
    def freeRewards(self):
        return self._getViewModel(8)

    @property
    def paidRewards(self):
        return self._getViewModel(9)

    @property
    def postRewards(self):
        return self._getViewModel(10)

    def getShowIntro(self):
        return self._getBool(11)

    def setShowIntro(self, value):
        self._setBool(11, value)

    def getHasNewExtras(self):
        return self._getBool(12)

    def setHasNewExtras(self, value):
        self._setBool(12, value)

    def getExtrasOpened(self):
        return self._getNumber(13)

    def setExtrasOpened(self, value):
        self._setNumber(13, value)

    def getExtrasTotal(self):
        return self._getNumber(14)

    def setExtrasTotal(self, value):
        self._setNumber(14, value)

    def getHighlightVoting(self):
        return self._getBool(15)

    def setHighlightVoting(self, value):
        self._setBool(15, value)

    def getSeasonTime(self):
        return self._getString(16)

    def setSeasonTime(self, value):
        self._setString(16, value)

    def getCurrentPoints(self):
        return self._getNumber(17)

    def setCurrentPoints(self, value):
        self._setNumber(17, value)

    def getTotalPoints(self):
        return self._getNumber(18)

    def setTotalPoints(self, value):
        self._setNumber(18, value)

    def getPreviousAllPoints(self):
        return self._getNumber(19)

    def setPreviousAllPoints(self, value):
        self._setNumber(19, value)

    def getPreviousPoints(self):
        return self._getNumber(20)

    def setPreviousPoints(self, value):
        self._setNumber(20, value)

    def getPreviousLevel(self):
        return self._getNumber(21)

    def setPreviousLevel(self, value):
        self._setNumber(21, value)

    def getCurrentAllPoints(self):
        return self._getNumber(22)

    def setCurrentAllPoints(self, value):
        self._setNumber(22, value)

    def getIsPaused(self):
        return self._getBool(23)

    def setIsPaused(self, value):
        self._setBool(23, value)

    def getSellAnyLevelsUnlockTimeLeft(self):
        return self._getString(24)

    def setSellAnyLevelsUnlockTimeLeft(self, value):
        self._setString(24, value)

    def getSeasonTimeLeft(self):
        return self._getString(25)

    def setSeasonTimeLeft(self, value):
        self._setString(25, value)

    def getIsFinalOfferTime(self):
        return self._getBool(26)

    def setIsFinalOfferTime(self, value):
        self._setBool(26, value)

    def getShowBuyButtonBubble(self):
        return self._getBool(27)

    def setShowBuyButtonBubble(self, value):
        self._setBool(27, value)

    def getIsVisibleBuyButton(self):
        return self._getBool(28)

    def setIsVisibleBuyButton(self, value):
        self._setBool(28, value)

    def getShowBuyAnimations(self):
        return self._getBool(29)

    def setShowBuyAnimations(self, value):
        self._setBool(29, value)

    def getIsPlayerVoted(self):
        return self._getBool(30)

    def setIsPlayerVoted(self, value):
        self._setBool(30, value)

    def _initialize(self):
        super(BattlePassProgressionsViewModel, self)._initialize()
        self._addViewModelProperty('intro', BattlePassIntroViewModel())
        self._addViewModelProperty('freeRewards', UserListModel())
        self._addViewModelProperty('paidRewards', UserListModel())
        self._addViewModelProperty('postRewards', UserListModel())
        self._addBoolProperty('showIntro', False)
        self._addBoolProperty('hasNewExtras', False)
        self._addNumberProperty('extrasOpened', 0)
        self._addNumberProperty('extrasTotal', 0)
        self._addBoolProperty('highlightVoting', False)
        self._addStringProperty('seasonTime', '')
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('totalPoints', 0)
        self._addNumberProperty('previousAllPoints', 0)
        self._addNumberProperty('previousPoints', 0)
        self._addNumberProperty('previousLevel', 0)
        self._addNumberProperty('currentAllPoints', 0)
        self._addBoolProperty('isPaused', False)
        self._addStringProperty('sellAnyLevelsUnlockTimeLeft', '')
        self._addStringProperty('seasonTimeLeft', '')
        self._addBoolProperty('isFinalOfferTime', False)
        self._addBoolProperty('showBuyButtonBubble', False)
        self._addBoolProperty('isVisibleBuyButton', False)
        self._addBoolProperty('showBuyAnimations', False)
        self._addBoolProperty('isPlayerVoted', False)
        self.onClose = self._addCommand('onClose')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onInfoBtnClick = self._addCommand('onInfoBtnClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onExtrasClick = self._addCommand('onExtrasClick')
        self.onVotingResultClick = self._addCommand('onVotingResultClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
