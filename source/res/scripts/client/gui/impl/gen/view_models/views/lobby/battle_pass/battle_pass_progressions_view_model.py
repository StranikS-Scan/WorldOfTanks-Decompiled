# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_progressions_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_off_season_view_model import BattlePassOffSeasonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_widget_3d_style_view_model import BattlePassWidget3DStyleViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.buy_button_model import BuyButtonModel
from gui.impl.gen.view_models.views.lobby.battle_pass.character_widget_view_model import CharacterWidgetViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel

class BattlePassProgressionsViewModel(CommonViewModel):
    __slots__ = ('onClose', 'onAboutClick', 'onBuyClick', 'onTakeClick', 'onTakeAllClick', 'onOpenShopClick', 'onPointsInfoClick', 'onFinishedAnimation', 'onGoToChapter', 'onViewLoaded')

    def __init__(self, properties=39, commands=11):
        super(BattlePassProgressionsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def intro(self):
        return self._getViewModel(4)

    @property
    def offSeason(self):
        return self._getViewModel(5)

    @property
    def buyButton(self):
        return self._getViewModel(6)

    @property
    def freeRewards(self):
        return self._getViewModel(7)

    @property
    def paidRewards(self):
        return self._getViewModel(8)

    @property
    def chapterCharacter(self):
        return self._getViewModel(9)

    @property
    def widget3dStyle(self):
        return self._getViewModel(10)

    def getShowIntro(self):
        return self._getBool(11)

    def setShowIntro(self, value):
        self._setBool(11, value)

    def getShowOffSeason(self):
        return self._getBool(12)

    def setShowOffSeason(self, value):
        self._setBool(12, value)

    def getSeasonText(self):
        return self._getString(13)

    def setSeasonText(self, value):
        self._setString(13, value)

    def getChapterText(self):
        return self._getString(14)

    def setChapterText(self, value):
        self._setString(14, value)

    def getCurrentPoints(self):
        return self._getNumber(15)

    def setCurrentPoints(self, value):
        self._setNumber(15, value)

    def getTotalPoints(self):
        return self._getNumber(16)

    def setTotalPoints(self, value):
        self._setNumber(16, value)

    def getPreviousAllPoints(self):
        return self._getNumber(17)

    def setPreviousAllPoints(self, value):
        self._setNumber(17, value)

    def getPreviousPoints(self):
        return self._getNumber(18)

    def setPreviousPoints(self, value):
        self._setNumber(18, value)

    def getPreviousLevel(self):
        return self._getNumber(19)

    def setPreviousLevel(self, value):
        self._setNumber(19, value)

    def getCurrentAllPoints(self):
        return self._getNumber(20)

    def setCurrentAllPoints(self, value):
        self._setNumber(20, value)

    def getPointsBeforeStart(self):
        return self._getNumber(21)

    def setPointsBeforeStart(self, value):
        self._setNumber(21, value)

    def getIsPaused(self):
        return self._getBool(22)

    def setIsPaused(self, value):
        self._setBool(22, value)

    def getSeasonTimeLeft(self):
        return self._getString(23)

    def setSeasonTimeLeft(self, value):
        self._setString(23, value)

    def getIsVisibleBuyButton(self):
        return self._getBool(24)

    def setIsVisibleBuyButton(self, value):
        self._setBool(24, value)

    def getShowBuyAnimations(self):
        return self._getBool(25)

    def setShowBuyAnimations(self, value):
        self._setBool(25, value)

    def getShowLevelsAnimations(self):
        return self._getBool(26)

    def setShowLevelsAnimations(self, value):
        self._setBool(26, value)

    def getProgressionState(self):
        return self._getString(27)

    def setProgressionState(self, value):
        self._setString(27, value)

    def getIsChooseDeviceEnabled(self):
        return self._getBool(28)

    def setIsChooseDeviceEnabled(self, value):
        self._setBool(28, value)

    def getAreSoundsAllowed(self):
        return self._getBool(29)

    def setAreSoundsAllowed(self, value):
        self._setBool(29, value)

    def getChapterCount(self):
        return self._getNumber(30)

    def setChapterCount(self, value):
        self._setNumber(30, value)

    def getChapterStep(self):
        return self._getNumber(31)

    def setChapterStep(self, value):
        self._setNumber(31, value)

    def getCurrentChapter(self):
        return self._getNumber(32)

    def setCurrentChapter(self, value):
        self._setNumber(32, value)

    def getChosenChapter(self):
        return self._getNumber(33)

    def setChosenChapter(self, value):
        self._setNumber(33, value)

    def getIsTakeAllButtonVisible(self):
        return self._getBool(34)

    def setIsTakeAllButtonVisible(self, value):
        self._setBool(34, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(35)

    def setNotChosenRewardCount(self, value):
        self._setNumber(35, value)

    def getBpcoinCount(self):
        return self._getNumber(36)

    def setBpcoinCount(self, value):
        self._setNumber(36, value)

    def getIsWalletAvailable(self):
        return self._getBool(37)

    def setIsWalletAvailable(self, value):
        self._setBool(37, value)

    def getShowReplaceRewardsAnimations(self):
        return self._getBool(38)

    def setShowReplaceRewardsAnimations(self, value):
        self._setBool(38, value)

    def _initialize(self):
        super(BattlePassProgressionsViewModel, self)._initialize()
        self._addViewModelProperty('intro', BattlePassIntroViewModel())
        self._addViewModelProperty('offSeason', BattlePassOffSeasonViewModel())
        self._addViewModelProperty('buyButton', BuyButtonModel())
        self._addViewModelProperty('freeRewards', UserListModel())
        self._addViewModelProperty('paidRewards', UserListModel())
        self._addViewModelProperty('chapterCharacter', CharacterWidgetViewModel())
        self._addViewModelProperty('widget3dStyle', BattlePassWidget3DStyleViewModel())
        self._addBoolProperty('showIntro', False)
        self._addBoolProperty('showOffSeason', False)
        self._addStringProperty('seasonText', '')
        self._addStringProperty('chapterText', '')
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('totalPoints', 0)
        self._addNumberProperty('previousAllPoints', 0)
        self._addNumberProperty('previousPoints', 0)
        self._addNumberProperty('previousLevel', 0)
        self._addNumberProperty('currentAllPoints', 0)
        self._addNumberProperty('pointsBeforeStart', 0)
        self._addBoolProperty('isPaused', False)
        self._addStringProperty('seasonTimeLeft', '')
        self._addBoolProperty('isVisibleBuyButton', False)
        self._addBoolProperty('showBuyAnimations', False)
        self._addBoolProperty('showLevelsAnimations', False)
        self._addStringProperty('progressionState', 'normalState')
        self._addBoolProperty('isChooseDeviceEnabled', True)
        self._addBoolProperty('areSoundsAllowed', True)
        self._addNumberProperty('chapterCount', 1)
        self._addNumberProperty('chapterStep', 1)
        self._addNumberProperty('currentChapter', 1)
        self._addNumberProperty('chosenChapter', 1)
        self._addBoolProperty('isTakeAllButtonVisible', False)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addNumberProperty('bpcoinCount', 0)
        self._addBoolProperty('isWalletAvailable', True)
        self._addBoolProperty('showReplaceRewardsAnimations', False)
        self.onClose = self._addCommand('onClose')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onTakeClick = self._addCommand('onTakeClick')
        self.onTakeAllClick = self._addCommand('onTakeAllClick')
        self.onOpenShopClick = self._addCommand('onOpenShopClick')
        self.onPointsInfoClick = self._addCommand('onPointsInfoClick')
        self.onFinishedAnimation = self._addCommand('onFinishedAnimation')
        self.onGoToChapter = self._addCommand('onGoToChapter')
        self.onViewLoaded = self._addCommand('onViewLoaded')
