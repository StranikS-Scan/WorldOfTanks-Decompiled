# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_main_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_chapter_model import ArmoryYardChapterModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_level_model import ArmoryYardLevelModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_quest_sub_model import ArmoryYardQuestSubModel

class State(Enum):
    BEFOREPROGRESSION = 'beforeProgression'
    ACTIVE = 'active'
    PURCHASESTAGE = 'purchaseStage'
    COMPLETED = 'completed'
    DISABLED = 'disabled'
    INTRO = 'intro'


class AnimationStatus(IntEnum):
    DISABLED = 0
    ACTIVE = 1


class RewardStatus(IntEnum):
    EMPTYREWARDS = 0
    READYREWARDS = 1
    ANIMATEDREWARDS = 2


class TabId(IntEnum):
    PROGRESS = 0
    QUESTS = 1
    SHOP = 2


class EscSource(IntEnum):
    KEYBOARD = 0
    MOUSE = 1


class SimpleTooltipStates(IntEnum):
    TAB = 0
    CHAPTER = 1
    SHOPINFO = 2
    STEP = 3


class BuyButtonState(IntEnum):
    HIDDEN = 0
    TOKENS = 1
    COINS = 2


class ArmoryYardMainViewModel(ViewModel):
    __slots__ = ('onMoveSpace', 'onStartMoving', 'onTabChange', 'onClose', 'onPlayAnimation', 'onSkipAnimation', 'onAboutEvent', 'onCollectReward', 'onBuyTokens', 'onShowVehiclePreview', 'onShowStylePreview', 'onShopOpen', 'onPlayStageSound', 'onQuestReroll', 'onChapterSelect')
    TOOLTIP_ID_ARG = 'tooltipId'
    FINAL_REWARD_TOOLTIP_TYPE = 'finalReward'

    def __init__(self, properties=25, commands=15):
        super(ArmoryYardMainViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getTabId(self):
        return TabId(self._getNumber(1))

    def setTabId(self, value):
        self._setNumber(1, value.value)

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getStartStepOfPostProgression(self):
        return self._getNumber(3)

    def setStartStepOfPostProgression(self, value):
        self._setNumber(3, value)

    def getViewedLevel(self):
        return self._getNumber(4)

    def setViewedLevel(self, value):
        self._setNumber(4, value)

    def getRewardStatus(self):
        return RewardStatus(self._getNumber(5))

    def setRewardStatus(self, value):
        self._setNumber(5, value.value)

    def getChapters(self):
        return self._getArray(6)

    def setChapters(self, value):
        self._setArray(6, value)

    @staticmethod
    def getChaptersType():
        return ArmoryYardChapterModel

    def getLevels(self):
        return self._getArray(7)

    def setLevels(self, value):
        self._setArray(7, value)

    @staticmethod
    def getLevelsType():
        return ArmoryYardLevelModel

    def getQuests(self):
        return self._getArray(8)

    def setQuests(self, value):
        self._setArray(8, value)

    @staticmethod
    def getQuestsType():
        return ArmoryYardQuestSubModel

    def getAnimationLevel(self):
        return self._getNumber(9)

    def setAnimationLevel(self, value):
        self._setNumber(9, value)

    def getLevelDuration(self):
        return self._getNumber(10)

    def setLevelDuration(self, value):
        self._setNumber(10, value)

    def getFromTimestamp(self):
        return self._getNumber(11)

    def setFromTimestamp(self, value):
        self._setNumber(11, value)

    def getToTimestamp(self):
        return self._getNumber(12)

    def setToTimestamp(self, value):
        self._setNumber(12, value)

    def getReceivedTokensCount(self):
        return self._getNumber(13)

    def setReceivedTokensCount(self, value):
        self._setNumber(13, value)

    def getTotalTokensCount(self):
        return self._getNumber(14)

    def setTotalTokensCount(self, value):
        self._setNumber(14, value)

    def getMaxNumberOfSteps(self):
        return self._getNumber(15)

    def setMaxNumberOfSteps(self, value):
        self._setNumber(15, value)

    def getAnimationStatus(self):
        return AnimationStatus(self._getNumber(16))

    def setAnimationStatus(self, value):
        self._setNumber(16, value.value)

    def getReplay(self):
        return self._getBool(17)

    def setReplay(self, value):
        self._setBool(17, value)

    def getShopButtonVisible(self):
        return self._getBool(18)

    def setShopButtonVisible(self, value):
        self._setBool(18, value)

    def getBuyButtonState(self):
        return BuyButtonState(self._getNumber(19))

    def setBuyButtonState(self, value):
        self._setNumber(19, value.value)

    def getFreeRerollCount(self):
        return self._getNumber(20)

    def setFreeRerollCount(self, value):
        self._setNumber(20, value)

    def getRerollCountDown(self):
        return self._getNumber(21)

    def setRerollCountDown(self, value):
        self._setNumber(21, value)

    def getIsRerollEnabled(self):
        return self._getBool(22)

    def setIsRerollEnabled(self, value):
        self._setBool(22, value)

    def getIsRerollButtonTriggerEnabled(self):
        return self._getBool(23)

    def setIsRerollButtonTriggerEnabled(self, value):
        self._setBool(23, value)

    def getIsPostProgression(self):
        return self._getBool(24)

    def setIsPostProgression(self, value):
        self._setBool(24, value)

    def _initialize(self):
        super(ArmoryYardMainViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('tabId')
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('startStepOfPostProgression', 0)
        self._addNumberProperty('viewedLevel', 0)
        self._addNumberProperty('rewardStatus')
        self._addArrayProperty('chapters', Array())
        self._addArrayProperty('levels', Array())
        self._addArrayProperty('quests', Array())
        self._addNumberProperty('animationLevel', 0)
        self._addNumberProperty('levelDuration', 0)
        self._addNumberProperty('fromTimestamp', 0)
        self._addNumberProperty('toTimestamp', 0)
        self._addNumberProperty('receivedTokensCount', 0)
        self._addNumberProperty('totalTokensCount', 0)
        self._addNumberProperty('maxNumberOfSteps', 0)
        self._addNumberProperty('animationStatus')
        self._addBoolProperty('replay', False)
        self._addBoolProperty('shopButtonVisible', False)
        self._addNumberProperty('buyButtonState')
        self._addNumberProperty('freeRerollCount', 0)
        self._addNumberProperty('rerollCountDown', 0)
        self._addBoolProperty('isRerollEnabled', False)
        self._addBoolProperty('isRerollButtonTriggerEnabled', False)
        self._addBoolProperty('isPostProgression', False)
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStartMoving = self._addCommand('onStartMoving')
        self.onTabChange = self._addCommand('onTabChange')
        self.onClose = self._addCommand('onClose')
        self.onPlayAnimation = self._addCommand('onPlayAnimation')
        self.onSkipAnimation = self._addCommand('onSkipAnimation')
        self.onAboutEvent = self._addCommand('onAboutEvent')
        self.onCollectReward = self._addCommand('onCollectReward')
        self.onBuyTokens = self._addCommand('onBuyTokens')
        self.onShowVehiclePreview = self._addCommand('onShowVehiclePreview')
        self.onShowStylePreview = self._addCommand('onShowStylePreview')
        self.onShopOpen = self._addCommand('onShopOpen')
        self.onPlayStageSound = self._addCommand('onPlayStageSound')
        self.onQuestReroll = self._addCommand('onQuestReroll')
        self.onChapterSelect = self._addCommand('onChapterSelect')
