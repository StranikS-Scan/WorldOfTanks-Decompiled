# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_progressions_view_model.py
from enum import Enum
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_off_season_view_model import BattlePassOffSeasonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_widget_3d_style_view_model import BattlePassWidget3DStyleViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel

class ChapterStates(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'


class ButtonStates(Enum):
    HIDE = 'hide'
    BUY = 'buy'
    LEVEL = 'level'
    ACTIVATE = 'activate'


class BattlePassProgressionsViewModel(CommonViewModel):
    __slots__ = ('onClose', 'onActionClick', 'onTakeClick', 'onTakeAllClick', 'onOpenShopClick', 'onAboutClick', 'onPointsInfoClick', 'onBpbitClick', 'onBpcoinClick', 'onTakeRewardsClick', 'onFinishedAnimation', 'onLevelsAnimationFinished', 'onChapterChoice', 'onViewLoaded')

    def __init__(self, properties=37, commands=15):
        super(BattlePassProgressionsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def offSeason(self):
        return self._getViewModel(4)

    @property
    def levels(self):
        return self._getViewModel(5)

    @property
    def widget3dStyle(self):
        return self._getViewModel(6)

    def getChapterID(self):
        return self._getNumber(7)

    def setChapterID(self, value):
        self._setNumber(7, value)

    def getChapterState(self):
        return ChapterStates(self._getString(8))

    def setChapterState(self, value):
        self._setString(8, value.value)

    def getShowOffSeason(self):
        return self._getBool(9)

    def setShowOffSeason(self, value):
        self._setBool(9, value)

    def getSeasonText(self):
        return self._getString(10)

    def setSeasonText(self, value):
        self._setString(10, value)

    def getSeasonTimeLeft(self):
        return self._getString(11)

    def setSeasonTimeLeft(self, value):
        self._setString(11, value)

    def getPreviousPointsInChapter(self):
        return self._getNumber(12)

    def setPreviousPointsInChapter(self, value):
        self._setNumber(12, value)

    def getCurrentPointsInChapter(self):
        return self._getNumber(13)

    def setCurrentPointsInChapter(self, value):
        self._setNumber(13, value)

    def getPreviousFreePointsInChapter(self):
        return self._getNumber(14)

    def setPreviousFreePointsInChapter(self, value):
        self._setNumber(14, value)

    def getFreePointsInChapter(self):
        return self._getNumber(15)

    def setFreePointsInChapter(self, value):
        self._setNumber(15, value)

    def getPreviousPointsInLevel(self):
        return self._getNumber(16)

    def setPreviousPointsInLevel(self, value):
        self._setNumber(16, value)

    def getCurrentPointsInLevel(self):
        return self._getNumber(17)

    def setCurrentPointsInLevel(self, value):
        self._setNumber(17, value)

    def getPreviousFreePointsInLevel(self):
        return self._getNumber(18)

    def setPreviousFreePointsInLevel(self, value):
        self._setNumber(18, value)

    def getFreePointsInLevel(self):
        return self._getNumber(19)

    def setFreePointsInLevel(self, value):
        self._setNumber(19, value)

    def getBpbitCount(self):
        return self._getNumber(20)

    def setBpbitCount(self, value):
        self._setNumber(20, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(21)

    def setNotChosenRewardCount(self, value):
        self._setNumber(21, value)

    def getIsBattlePassCompleted(self):
        return self._getBool(22)

    def setIsBattlePassCompleted(self, value):
        self._setBool(22, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(23)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(23, value)

    def getPreviousLevel(self):
        return self._getNumber(24)

    def setPreviousLevel(self, value):
        self._setNumber(24, value)

    def getPotentialLevel(self):
        return self._getNumber(25)

    def setPotentialLevel(self, value):
        self._setNumber(25, value)

    def getPreviousPotentialLevel(self):
        return self._getNumber(26)

    def setPreviousPotentialLevel(self, value):
        self._setNumber(26, value)

    def getIsPaused(self):
        return self._getBool(27)

    def setIsPaused(self, value):
        self._setBool(27, value)

    def getIsChooseDeviceEnabled(self):
        return self._getBool(28)

    def setIsChooseDeviceEnabled(self, value):
        self._setBool(28, value)

    def getBpcoinCount(self):
        return self._getNumber(29)

    def setBpcoinCount(self, value):
        self._setNumber(29, value)

    def getIsWalletAvailable(self):
        return self._getBool(30)

    def setIsWalletAvailable(self, value):
        self._setBool(30, value)

    def getShowBuyAnimations(self):
        return self._getBool(31)

    def setShowBuyAnimations(self, value):
        self._setBool(31, value)

    def getShowLevelsAnimations(self):
        return self._getBool(32)

    def setShowLevelsAnimations(self, value):
        self._setBool(32, value)

    def getShowReplaceRewardsAnimations(self):
        return self._getBool(33)

    def setShowReplaceRewardsAnimations(self, value):
        self._setBool(33, value)

    def getButtonState(self):
        return ButtonStates(self._getString(34))

    def setButtonState(self, value):
        self._setString(34, value.value)

    def getIsStyleTaken(self):
        return self._getBool(35)

    def setIsStyleTaken(self, value):
        self._setBool(35, value)

    def getIsSeasonEndingSoon(self):
        return self._getBool(36)

    def setIsSeasonEndingSoon(self, value):
        self._setBool(36, value)

    def _initialize(self):
        super(BattlePassProgressionsViewModel, self)._initialize()
        self._addViewModelProperty('offSeason', BattlePassOffSeasonViewModel())
        self._addViewModelProperty('levels', UserListModel())
        self._addViewModelProperty('widget3dStyle', BattlePassWidget3DStyleViewModel())
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('chapterState')
        self._addBoolProperty('showOffSeason', False)
        self._addStringProperty('seasonText', '')
        self._addStringProperty('seasonTimeLeft', '')
        self._addNumberProperty('previousPointsInChapter', 0)
        self._addNumberProperty('currentPointsInChapter', 0)
        self._addNumberProperty('previousFreePointsInChapter', 0)
        self._addNumberProperty('freePointsInChapter', 0)
        self._addNumberProperty('previousPointsInLevel', 0)
        self._addNumberProperty('currentPointsInLevel', 0)
        self._addNumberProperty('previousFreePointsInLevel', 0)
        self._addNumberProperty('freePointsInLevel', 0)
        self._addNumberProperty('bpbitCount', 0)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addBoolProperty('isBattlePassCompleted', False)
        self._addBoolProperty('isChooseRewardsEnabled', True)
        self._addNumberProperty('previousLevel', 0)
        self._addNumberProperty('potentialLevel', 0)
        self._addNumberProperty('previousPotentialLevel', 0)
        self._addBoolProperty('isPaused', False)
        self._addBoolProperty('isChooseDeviceEnabled', True)
        self._addNumberProperty('bpcoinCount', 0)
        self._addBoolProperty('isWalletAvailable', True)
        self._addBoolProperty('showBuyAnimations', False)
        self._addBoolProperty('showLevelsAnimations', False)
        self._addBoolProperty('showReplaceRewardsAnimations', False)
        self._addStringProperty('buttonState')
        self._addBoolProperty('isStyleTaken', False)
        self._addBoolProperty('isSeasonEndingSoon', False)
        self.onClose = self._addCommand('onClose')
        self.onActionClick = self._addCommand('onActionClick')
        self.onTakeClick = self._addCommand('onTakeClick')
        self.onTakeAllClick = self._addCommand('onTakeAllClick')
        self.onOpenShopClick = self._addCommand('onOpenShopClick')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onPointsInfoClick = self._addCommand('onPointsInfoClick')
        self.onBpbitClick = self._addCommand('onBpbitClick')
        self.onBpcoinClick = self._addCommand('onBpcoinClick')
        self.onTakeRewardsClick = self._addCommand('onTakeRewardsClick')
        self.onFinishedAnimation = self._addCommand('onFinishedAnimation')
        self.onLevelsAnimationFinished = self._addCommand('onLevelsAnimationFinished')
        self.onChapterChoice = self._addCommand('onChapterChoice')
        self.onViewLoaded = self._addCommand('onViewLoaded')
