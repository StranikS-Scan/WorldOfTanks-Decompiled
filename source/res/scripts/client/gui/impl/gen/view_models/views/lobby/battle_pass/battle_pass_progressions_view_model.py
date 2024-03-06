# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_progressions_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.awards_widget_model import AwardsWidgetModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_off_season_view_model import BattlePassOffSeasonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_widget_3d_style_view_model import BattlePassWidget3DStyleViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_widget_final_rewards_view_model import BattlePassWidgetFinalRewardsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.character_widget_view_model import CharacterWidgetViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.common_view_model import CommonViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel

class ChapterStates(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    NOTSTARTED = 'notStarted'


class ActionTypes(Enum):
    NOACTION = 'noAction'
    BUY = 'buy'
    BUYLEVEL = 'buyLevel'
    ACTIVATECHAPTER = 'activateChapter'


class ChapterType(Enum):
    COMMON = 'common'
    EXTRA = 'extra'
    HOLIDAY = 'holiday'


class BattlePassProgressionsViewModel(CommonViewModel):
    __slots__ = ('onClose', 'onActionClick', 'onTakeClick', 'onTakeAllClick', 'onOpenShopClick', 'onAboutClick', 'onPointsInfoClick', 'onFinishedAnimation', 'onLevelsAnimationFinished', 'showTankmen', 'onChapterChoice', 'onViewLoaded')

    def __init__(self, properties=41, commands=13):
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
    def widgetFinalRewards(self):
        return self._getViewModel(8)

    @staticmethod
    def getWidgetFinalRewardsType():
        return BattlePassWidgetFinalRewardsViewModel

    @property
    def awardsWidget(self):
        return self._getViewModel(9)

    @staticmethod
    def getAwardsWidgetType():
        return AwardsWidgetModel

    @property
    def price(self):
        return self._getViewModel(10)

    @staticmethod
    def getPriceType():
        return UserCompoundPriceModel

    def getChapterID(self):
        return self._getNumber(11)

    def setChapterID(self, value):
        self._setNumber(11, value)

    def getChapterState(self):
        return ChapterStates(self._getString(12))

    def setChapterState(self, value):
        self._setString(12, value.value)

    def getFreeFinalRewards(self):
        return self._getArray(13)

    def setFreeFinalRewards(self, value):
        self._setArray(13, value)

    @staticmethod
    def getFreeFinalRewardsType():
        return unicode

    def getPaidFinalRewards(self):
        return self._getArray(14)

    def setPaidFinalRewards(self, value):
        self._setArray(14, value)

    @staticmethod
    def getPaidFinalRewardsType():
        return unicode

    def getShowOffSeason(self):
        return self._getBool(15)

    def setShowOffSeason(self, value):
        self._setBool(15, value)

    def getPreviousPointsInChapter(self):
        return self._getNumber(16)

    def setPreviousPointsInChapter(self, value):
        self._setNumber(16, value)

    def getCurrentPointsInChapter(self):
        return self._getNumber(17)

    def setCurrentPointsInChapter(self, value):
        self._setNumber(17, value)

    def getPreviousFreePointsInChapter(self):
        return self._getNumber(18)

    def setPreviousFreePointsInChapter(self, value):
        self._setNumber(18, value)

    def getFreePointsInChapter(self):
        return self._getNumber(19)

    def setFreePointsInChapter(self, value):
        self._setNumber(19, value)

    def getPreviousPointsInLevel(self):
        return self._getNumber(20)

    def setPreviousPointsInLevel(self, value):
        self._setNumber(20, value)

    def getCurrentPointsInLevel(self):
        return self._getNumber(21)

    def setCurrentPointsInLevel(self, value):
        self._setNumber(21, value)

    def getPreviousFreePointsInLevel(self):
        return self._getNumber(22)

    def setPreviousFreePointsInLevel(self, value):
        self._setNumber(22, value)

    def getFreePointsInLevel(self):
        return self._getNumber(23)

    def setFreePointsInLevel(self, value):
        self._setNumber(23, value)

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

    def getIsWalletAvailable(self):
        return self._getBool(29)

    def setIsWalletAvailable(self, value):
        self._setBool(29, value)

    def getShowBuyAnimations(self):
        return self._getBool(30)

    def setShowBuyAnimations(self, value):
        self._setBool(30, value)

    def getShowLevelsAnimations(self):
        return self._getBool(31)

    def setShowLevelsAnimations(self, value):
        self._setBool(31, value)

    def getShowReplaceRewardsAnimations(self):
        return self._getBool(32)

    def setShowReplaceRewardsAnimations(self, value):
        self._setBool(32, value)

    def getActionType(self):
        return ActionTypes(self._getString(33))

    def setActionType(self, value):
        self._setString(33, value.value)

    def getIsStyleTaken(self):
        return self._getBool(34)

    def setIsStyleTaken(self, value):
        self._setBool(34, value)

    def getIsSeasonEndingSoon(self):
        return self._getBool(35)

    def setIsSeasonEndingSoon(self, value):
        self._setBool(35, value)

    def getChapterType(self):
        return ChapterType(self._getString(36))

    def setChapterType(self, value):
        self._setString(36, value.value)

    def getHasExtra(self):
        return self._getBool(37)

    def setHasExtra(self, value):
        self._setBool(37, value)

    def getExpireTime(self):
        return self._getNumber(38)

    def setExpireTime(self, value):
        self._setNumber(38, value)

    def getTimeLeft(self):
        return self._getNumber(39)

    def setTimeLeft(self, value):
        self._setNumber(39, value)

    def getSeasonNum(self):
        return self._getNumber(40)

    def setSeasonNum(self, value):
        self._setNumber(40, value)

    def _initialize(self):
        super(BattlePassProgressionsViewModel, self)._initialize()
        self._addViewModelProperty('offSeason', BattlePassOffSeasonViewModel())
        self._addViewModelProperty('levels', UserListModel())
        self._addViewModelProperty('widget3dStyle', BattlePassWidget3DStyleViewModel())
        self._addViewModelProperty('chapterCharacter', CharacterWidgetViewModel())
        self._addViewModelProperty('widgetFinalRewards', BattlePassWidgetFinalRewardsViewModel())
        self._addViewModelProperty('awardsWidget', AwardsWidgetModel())
        self._addViewModelProperty('price', UserCompoundPriceModel())
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('chapterState')
        self._addArrayProperty('freeFinalRewards', Array())
        self._addArrayProperty('paidFinalRewards', Array())
        self._addBoolProperty('showOffSeason', False)
        self._addNumberProperty('previousPointsInChapter', 0)
        self._addNumberProperty('currentPointsInChapter', 0)
        self._addNumberProperty('previousFreePointsInChapter', 0)
        self._addNumberProperty('freePointsInChapter', 0)
        self._addNumberProperty('previousPointsInLevel', 0)
        self._addNumberProperty('currentPointsInLevel', 0)
        self._addNumberProperty('previousFreePointsInLevel', 0)
        self._addNumberProperty('freePointsInLevel', 0)
        self._addNumberProperty('previousLevel', 0)
        self._addNumberProperty('potentialLevel', 0)
        self._addNumberProperty('previousPotentialLevel', 0)
        self._addBoolProperty('isPaused', False)
        self._addBoolProperty('isChooseDeviceEnabled', True)
        self._addBoolProperty('isWalletAvailable', True)
        self._addBoolProperty('showBuyAnimations', False)
        self._addBoolProperty('showLevelsAnimations', False)
        self._addBoolProperty('showReplaceRewardsAnimations', False)
        self._addStringProperty('actionType')
        self._addBoolProperty('isStyleTaken', False)
        self._addBoolProperty('isSeasonEndingSoon', False)
        self._addStringProperty('chapterType')
        self._addBoolProperty('hasExtra', False)
        self._addNumberProperty('expireTime', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addNumberProperty('seasonNum', 0)
        self.onClose = self._addCommand('onClose')
        self.onActionClick = self._addCommand('onActionClick')
        self.onTakeClick = self._addCommand('onTakeClick')
        self.onTakeAllClick = self._addCommand('onTakeAllClick')
        self.onOpenShopClick = self._addCommand('onOpenShopClick')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onPointsInfoClick = self._addCommand('onPointsInfoClick')
        self.onFinishedAnimation = self._addCommand('onFinishedAnimation')
        self.onLevelsAnimationFinished = self._addCommand('onLevelsAnimationFinished')
        self.showTankmen = self._addCommand('showTankmen')
        self.onChapterChoice = self._addCommand('onChapterChoice')
        self.onViewLoaded = self._addCommand('onViewLoaded')
