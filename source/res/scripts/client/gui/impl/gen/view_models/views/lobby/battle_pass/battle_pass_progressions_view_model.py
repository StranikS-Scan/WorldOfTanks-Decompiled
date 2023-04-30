# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_progressions_view_model.py
from enum import Enum
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_off_season_view_model import BattlePassOffSeasonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_widget_3d_style_view_model import BattlePassWidget3DStyleViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.character_widget_view_model import CharacterWidgetViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.collection_entry_point_view_model import CollectionEntryPointViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel

class ChapterStates(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    NOTSTARTED = 'notStarted'


class ButtonStates(Enum):
    HIDE = 'hide'
    BUY = 'buy'
    LEVEL = 'level'
    ACTIVATE = 'activate'


class BattlePassProgressionsViewModel(CommonViewModel):
    __slots__ = ('onClose', 'onActionClick', 'onTakeClick', 'onTakeAllClick', 'onOpenShopClick', 'onAboutClick', 'onPointsInfoClick', 'onBpbitClick', 'onBpcoinClick', 'onTakeRewardsClick', 'onFinishedAnimation', 'onLevelsAnimationFinished', 'onChapterChoice', 'onViewLoaded')

    def __init__(self, properties=43, commands=15):
        super(BattlePassProgressionsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def offSeason(self):
        return self._getViewModel(4)

    @staticmethod
    def getOffSeasonType():
        return BattlePassOffSeasonViewModel

    @property
    def levels(self):
        return self._getViewModel(5)

    @staticmethod
    def getLevelsType():
        return RewardLevelModel

    @property
    def widget3dStyle(self):
        return self._getViewModel(6)

    @staticmethod
    def getWidget3dStyleType():
        return BattlePassWidget3DStyleViewModel

    @property
    def chapterCharacter(self):
        return self._getViewModel(7)

    @staticmethod
    def getChapterCharacterType():
        return CharacterWidgetViewModel

    @property
    def collectionEntryPoint(self):
        return self._getViewModel(8)

    @staticmethod
    def getCollectionEntryPointType():
        return CollectionEntryPointViewModel

    def getChapterID(self):
        return self._getNumber(9)

    def setChapterID(self, value):
        self._setNumber(9, value)

    def getChapterState(self):
        return ChapterStates(self._getString(10))

    def setChapterState(self, value):
        self._setString(10, value.value)

    def getFinalReward(self):
        return self._getString(11)

    def setFinalReward(self, value):
        self._setString(11, value)

    def getShowOffSeason(self):
        return self._getBool(12)

    def setShowOffSeason(self, value):
        self._setBool(12, value)

    def getSeasonText(self):
        return self._getString(13)

    def setSeasonText(self, value):
        self._setString(13, value)

    def getExpireTimeStr(self):
        return self._getString(14)

    def setExpireTimeStr(self, value):
        self._setString(14, value)

    def getPreviousPointsInChapter(self):
        return self._getNumber(15)

    def setPreviousPointsInChapter(self, value):
        self._setNumber(15, value)

    def getCurrentPointsInChapter(self):
        return self._getNumber(16)

    def setCurrentPointsInChapter(self, value):
        self._setNumber(16, value)

    def getPreviousFreePointsInChapter(self):
        return self._getNumber(17)

    def setPreviousFreePointsInChapter(self, value):
        self._setNumber(17, value)

    def getFreePointsInChapter(self):
        return self._getNumber(18)

    def setFreePointsInChapter(self, value):
        self._setNumber(18, value)

    def getPreviousPointsInLevel(self):
        return self._getNumber(19)

    def setPreviousPointsInLevel(self, value):
        self._setNumber(19, value)

    def getCurrentPointsInLevel(self):
        return self._getNumber(20)

    def setCurrentPointsInLevel(self, value):
        self._setNumber(20, value)

    def getPreviousFreePointsInLevel(self):
        return self._getNumber(21)

    def setPreviousFreePointsInLevel(self, value):
        self._setNumber(21, value)

    def getFreePointsInLevel(self):
        return self._getNumber(22)

    def setFreePointsInLevel(self, value):
        self._setNumber(22, value)

    def getBpbitCount(self):
        return self._getNumber(23)

    def setBpbitCount(self, value):
        self._setNumber(23, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(24)

    def setNotChosenRewardCount(self, value):
        self._setNumber(24, value)

    def getIsBattlePassCompleted(self):
        return self._getBool(25)

    def setIsBattlePassCompleted(self, value):
        self._setBool(25, value)

    def getIsChooseRewardsEnabled(self):
        return self._getBool(26)

    def setIsChooseRewardsEnabled(self, value):
        self._setBool(26, value)

    def getPreviousLevel(self):
        return self._getNumber(27)

    def setPreviousLevel(self, value):
        self._setNumber(27, value)

    def getPotentialLevel(self):
        return self._getNumber(28)

    def setPotentialLevel(self, value):
        self._setNumber(28, value)

    def getPreviousPotentialLevel(self):
        return self._getNumber(29)

    def setPreviousPotentialLevel(self, value):
        self._setNumber(29, value)

    def getIsPaused(self):
        return self._getBool(30)

    def setIsPaused(self, value):
        self._setBool(30, value)

    def getIsChooseDeviceEnabled(self):
        return self._getBool(31)

    def setIsChooseDeviceEnabled(self, value):
        self._setBool(31, value)

    def getBpcoinCount(self):
        return self._getNumber(32)

    def setBpcoinCount(self, value):
        self._setNumber(32, value)

    def getIsWalletAvailable(self):
        return self._getBool(33)

    def setIsWalletAvailable(self, value):
        self._setBool(33, value)

    def getShowBuyAnimations(self):
        return self._getBool(34)

    def setShowBuyAnimations(self, value):
        self._setBool(34, value)

    def getShowLevelsAnimations(self):
        return self._getBool(35)

    def setShowLevelsAnimations(self, value):
        self._setBool(35, value)

    def getShowReplaceRewardsAnimations(self):
        return self._getBool(36)

    def setShowReplaceRewardsAnimations(self, value):
        self._setBool(36, value)

    def getButtonState(self):
        return ButtonStates(self._getString(37))

    def setButtonState(self, value):
        self._setString(37, value.value)

    def getIsStyleTaken(self):
        return self._getBool(38)

    def setIsStyleTaken(self, value):
        self._setBool(38, value)

    def getIsSeasonEndingSoon(self):
        return self._getBool(39)

    def setIsSeasonEndingSoon(self, value):
        self._setBool(39, value)

    def getIsExtra(self):
        return self._getBool(40)

    def setIsExtra(self, value):
        self._setBool(40, value)

    def getHasExtra(self):
        return self._getBool(41)

    def setHasExtra(self, value):
        self._setBool(41, value)

    def getExpireTime(self):
        return self._getNumber(42)

    def setExpireTime(self, value):
        self._setNumber(42, value)

    def _initialize(self):
        super(BattlePassProgressionsViewModel, self)._initialize()
        self._addViewModelProperty('offSeason', BattlePassOffSeasonViewModel())
        self._addViewModelProperty('levels', UserListModel())
        self._addViewModelProperty('widget3dStyle', BattlePassWidget3DStyleViewModel())
        self._addViewModelProperty('chapterCharacter', CharacterWidgetViewModel())
        self._addViewModelProperty('collectionEntryPoint', CollectionEntryPointViewModel())
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('chapterState')
        self._addStringProperty('finalReward', '')
        self._addBoolProperty('showOffSeason', False)
        self._addStringProperty('seasonText', '')
        self._addStringProperty('expireTimeStr', '')
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
        self._addBoolProperty('isExtra', False)
        self._addBoolProperty('hasExtra', False)
        self._addNumberProperty('expireTime', 0)
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
