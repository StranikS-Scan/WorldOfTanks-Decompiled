# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_progressions_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_off_season_view_model import BattlePassOffSeasonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.buy_button_model import BuyButtonModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel

class BattlePassProgressionsViewModel(CommonViewModel):
    __slots__ = ('onClose', 'onAboutClick', 'onInfoBtnClick', 'onBuyClick', 'onBuyBtnClick', 'onExtrasClick', 'onVotingResultClick', 'onBuyVehicleClick', 'onTrophySelectClick', 'onNewDeviceSelectClick', 'onViewLoaded')
    LACK_OF_VEHICLES = 'lackOfVehiclesState'
    NORMAL = 'normalState'
    ONBOARDING = 'onboardingState'

    def __init__(self, properties=40, commands=12):
        super(BattlePassProgressionsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def intro(self):
        return self._getViewModel(7)

    @property
    def offSeason(self):
        return self._getViewModel(8)

    @property
    def buyButton(self):
        return self._getViewModel(9)

    @property
    def freeRewards(self):
        return self._getViewModel(10)

    @property
    def paidRewards(self):
        return self._getViewModel(11)

    @property
    def postRewards(self):
        return self._getViewModel(12)

    @property
    def medalReward(self):
        return self._getViewModel(13)

    def getShowIntro(self):
        return self._getBool(14)

    def setShowIntro(self, value):
        self._setBool(14, value)

    def getShowOffSeason(self):
        return self._getBool(15)

    def setShowOffSeason(self, value):
        self._setBool(15, value)

    def getHasNewExtras(self):
        return self._getBool(16)

    def setHasNewExtras(self, value):
        self._setBool(16, value)

    def getExtrasOpened(self):
        return self._getNumber(17)

    def setExtrasOpened(self, value):
        self._setNumber(17, value)

    def getExtrasTotal(self):
        return self._getNumber(18)

    def setExtrasTotal(self, value):
        self._setNumber(18, value)

    def getHighlightVoting(self):
        return self._getBool(19)

    def setHighlightVoting(self, value):
        self._setBool(19, value)

    def getSeasonTime(self):
        return self._getString(20)

    def setSeasonTime(self, value):
        self._setString(20, value)

    def getCurrentPoints(self):
        return self._getNumber(21)

    def setCurrentPoints(self, value):
        self._setNumber(21, value)

    def getTotalPoints(self):
        return self._getNumber(22)

    def setTotalPoints(self, value):
        self._setNumber(22, value)

    def getPreviousAllPoints(self):
        return self._getNumber(23)

    def setPreviousAllPoints(self, value):
        self._setNumber(23, value)

    def getPreviousPoints(self):
        return self._getNumber(24)

    def setPreviousPoints(self, value):
        self._setNumber(24, value)

    def getPreviousLevel(self):
        return self._getNumber(25)

    def setPreviousLevel(self, value):
        self._setNumber(25, value)

    def getCurrentAllPoints(self):
        return self._getNumber(26)

    def setCurrentAllPoints(self, value):
        self._setNumber(26, value)

    def getIsPaused(self):
        return self._getBool(27)

    def setIsPaused(self, value):
        self._setBool(27, value)

    def getSeasonTimeLeft(self):
        return self._getString(28)

    def setSeasonTimeLeft(self, value):
        self._setString(28, value)

    def getIsVisibleBuyButton(self):
        return self._getBool(29)

    def setIsVisibleBuyButton(self, value):
        self._setBool(29, value)

    def getShowBuyAnimations(self):
        return self._getBool(30)

    def setShowBuyAnimations(self, value):
        self._setBool(30, value)

    def getShowLevelsAnimations(self):
        return self._getBool(31)

    def setShowLevelsAnimations(self, value):
        self._setBool(31, value)

    def getIsPlayerVoted(self):
        return self._getBool(32)

    def setIsPlayerVoted(self, value):
        self._setBool(32, value)

    def getHaveMedalReward(self):
        return self._getBool(33)

    def setHaveMedalReward(self, value):
        self._setBool(33, value)

    def getCanPlayerParticipate(self):
        return self._getBool(34)

    def setCanPlayerParticipate(self, value):
        self._setBool(34, value)

    def getProgressionState(self):
        return self._getString(35)

    def setProgressionState(self, value):
        self._setString(35, value)

    def getTrophySelectCount(self):
        return self._getNumber(36)

    def setTrophySelectCount(self, value):
        self._setNumber(36, value)

    def getNewDeviceSelectCount(self):
        return self._getNumber(37)

    def setNewDeviceSelectCount(self, value):
        self._setNumber(37, value)

    def getIsChooseDeviceEnabled(self):
        return self._getBool(38)

    def setIsChooseDeviceEnabled(self, value):
        self._setBool(38, value)

    def getAreSoundsAllowed(self):
        return self._getBool(39)

    def setAreSoundsAllowed(self, value):
        self._setBool(39, value)

    def _initialize(self):
        super(BattlePassProgressionsViewModel, self)._initialize()
        self._addViewModelProperty('intro', BattlePassIntroViewModel())
        self._addViewModelProperty('offSeason', BattlePassOffSeasonViewModel())
        self._addViewModelProperty('buyButton', BuyButtonModel())
        self._addViewModelProperty('freeRewards', UserListModel())
        self._addViewModelProperty('paidRewards', UserListModel())
        self._addViewModelProperty('postRewards', UserListModel())
        self._addViewModelProperty('medalReward', UserListModel())
        self._addBoolProperty('showIntro', False)
        self._addBoolProperty('showOffSeason', False)
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
        self._addStringProperty('seasonTimeLeft', '')
        self._addBoolProperty('isVisibleBuyButton', False)
        self._addBoolProperty('showBuyAnimations', False)
        self._addBoolProperty('showLevelsAnimations', False)
        self._addBoolProperty('isPlayerVoted', False)
        self._addBoolProperty('haveMedalReward', False)
        self._addBoolProperty('canPlayerParticipate', True)
        self._addStringProperty('progressionState', 'normalState')
        self._addNumberProperty('trophySelectCount', 0)
        self._addNumberProperty('newDeviceSelectCount', 0)
        self._addBoolProperty('isChooseDeviceEnabled', True)
        self._addBoolProperty('areSoundsAllowed', True)
        self.onClose = self._addCommand('onClose')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onInfoBtnClick = self._addCommand('onInfoBtnClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onExtrasClick = self._addCommand('onExtrasClick')
        self.onVotingResultClick = self._addCommand('onVotingResultClick')
        self.onBuyVehicleClick = self._addCommand('onBuyVehicleClick')
        self.onTrophySelectClick = self._addCommand('onTrophySelectClick')
        self.onNewDeviceSelectClick = self._addCommand('onNewDeviceSelectClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
