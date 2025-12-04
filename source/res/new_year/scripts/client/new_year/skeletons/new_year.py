# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/skeletons/new_year.py
import typing
from adisp import adisp_async, adisp_process
from skeletons.gui.game_control import IFestivityController, IGameController, IFestivityTutorialController
if typing.TYPE_CHECKING:
    from Event import Event
    from ..tamagotchi.dto.leaderboard import Leaderboard
    from ..tamagotchi.dto.config import Config
    from ..tamagotchi.dto.player_info import PlayerInfo

class INewYearController(IFestivityController):
    onDataUpdated = None
    onUpdateSlot = None
    onSetHangToyEffectEnabled = None
    onVariadicDiscountsUpdated = None
    onCustomizationObjectUpdated = None
    onSpaceObjectHover = None
    onGUIObjectHover = None
    onNySettingsChanged = None
    onOnboardingFinished = None
    onUIControlsLockChanged = None
    onPetVisibilityUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isInProgress(self):
        raise NotImplementedError

    def isPostEvent(self):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isSuspended(self):
        raise NotImplementedError

    def isFirstEntrance(self):
        raise NotImplementedError

    def isOnboardingOpen(self):
        raise NotImplementedError

    def isMaxAtmosphereLevel(self):
        raise NotImplementedError

    def getHangarQuestsFlagData(self):
        raise NotImplementedError

    def getHangarWidgetLinkage(self):
        raise NotImplementedError

    def getHangarEdgeColor(self):
        raise NotImplementedError

    def getSlotDescrs(self):
        raise NotImplementedError

    def getToyDescr(self, toyID):
        raise NotImplementedError

    def getToyByID(self, toyID):
        raise NotImplementedError

    def getToysByType(self, slotID):
        raise NotImplementedError

    def getAllToysByTypeFromCache(self, typeID):
        raise NotImplementedError

    def getAllCollectedToysId(self, year=None):
        raise NotImplementedError

    @adisp_async
    def hangToy(self, toyID, slotID, callback=None):
        raise NotImplementedError

    @adisp_async
    def buyToy(self, toyID, callback=None):
        raise NotImplementedError

    def getLevel(self, level):
        raise NotImplementedError

    def checkForNewToys(self, slot=None, objectType=None):
        raise NotImplementedError

    def isCollectionCompleted(self, collectionID=None):
        raise NotImplementedError

    def getFinishTime(self):
        raise NotImplementedError

    def showStateMessage(self):
        raise NotImplementedError

    def sendSeenToys(self, toyIDs):
        raise NotImplementedError

    def sendSeenToysInCollection(self, toyIDs):
        raise NotImplementedError

    def sendViewAlbum(self, settingID, rank):
        raise NotImplementedError

    def getUniqueMegaToysCount(self):
        raise NotImplementedError

    def isFullRegularToysGroup(self, typeID, settingID, rank):
        raise NotImplementedError

    def isRegularToysCollected(self):
        raise NotImplementedError

    def getMaxToysStyle(self):
        raise NotImplementedError

    def getActiveSettingBonusValue(self):
        raise NotImplementedError

    def getMaxBonusValue(self):
        raise NotImplementedError

    def getVariadicDiscountCount(self):
        raise NotImplementedError

    def updateVariadicDiscounts(self):
        raise NotImplementedError

    def markPreviousYearTabVisited(self, yearName, settingsKey):
        raise NotImplementedError

    def getCollectionAwardQuest(self, collectionTypeToQuest, collectionType, filterFunc):
        raise NotImplementedError

    @property
    def tutorial(self):
        raise NotImplementedError

    def isWidgetVisible(self, prbState):
        raise NotImplementedError

    def isCreditBonusVisible(self, prbState):
        raise NotImplementedError

    def setSpaceObjectHover(self, gameObject, value):
        raise NotImplementedError

    def setGuiObjectHover(self, objectName, value):
        raise NotImplementedError

    def lockUIControls(self, lockID):
        raise NotImplementedError

    def unlockUIControls(self, lockID):
        raise NotImplementedError

    def isUIControlsLocked(self):
        raise NotImplementedError

    def isLootboxBigType(self, lbType):
        raise NotImplementedError

    def isLootboxTankType(self, lbType):
        raise NotImplementedError

    @adisp_async
    @adisp_process
    def switchToNewYearPrebattle(self, callback):
        raise NotImplementedError

    @adisp_process
    def switchFromNewYearPrebattle(self):
        raise NotImplementedError

    def isNewYearBattleMode(self):
        raise NotImplementedError

    @property
    def prbNewYearActionName(self):
        raise NotImplementedError

    def isCelebVoiceoverEnabled(self):
        raise NotImplementedError


class INewYearTutorialController(IFestivityTutorialController):
    pass


class INewYearSurpriseMachine(IGameController):
    onStateUpdate = None
    onMachineButtonPress = None
    onMachineSelectButtonPress = None
    onUpdateApplyCoin = None
    onMachineButtonHovered = None
    onActivationChanged = None
    onMachineBusyStatusUpdated = None

    @property
    def machineState(self):
        raise NotImplementedError

    @property
    def canApplyCoin(self):
        raise NotImplementedError

    @property
    def canBuyCoin(self):
        raise NotImplementedError

    @property
    def isMachineBusy(self):
        raise NotImplementedError

    @property
    def isMachineActivated(self):
        raise NotImplementedError

    @property
    def selectedBtnType(self):
        raise NotImplementedError

    def setState(self, state):
        raise NotImplementedError

    def setViewState(self, state):
        raise NotImplementedError

    def refreshApplyCoinState(self):
        raise NotImplementedError

    def updateSurpriseMachineBusyStatus(self, isBusy):
        raise NotImplementedError

    def tryActivateMachine(self):
        raise NotImplementedError

    def deactivateMachine(self):
        raise NotImplementedError

    def handleSurpriseMachineBtnPress(self, btnType):
        raise NotImplementedError

    def moveSelectionLeft(self):
        raise NotImplementedError

    def moveSelectionRight(self):
        raise NotImplementedError


class IRaccoonAnimationController(IGameController):
    __slots__ = ('onShowGift',)

    def __init__(self):
        super(IRaccoonAnimationController, self).__init__()
        self.onShowGift = None
        return

    def showLetterAction(self):
        raise NotImplementedError

    def releaseLetterAction(self):
        raise NotImplementedError

    def activateItem(self, name):
        raise NotImplementedError

    def updateMoodState(self, state):
        raise NotImplementedError

    def setAnimationsEnabled(self, enabled):
        raise NotImplementedError


class INewYearEnvironmentSwitchController(IGameController):
    onEnvironmentSwitched = None

    @property
    def userEnvState(self):
        raise NotImplementedError

    @property
    def needToShowTip(self):
        raise NotImplementedError

    @property
    def currentDayNightMode(self):
        raise NotImplementedError

    @property
    def currentAppliedDayNightMode(self):
        raise NotImplementedError

    def notifyTipShouldClose(self):
        raise NotImplementedError

    def skipSwitcherTip(self):
        raise NotImplementedError

    def applyCurrentEnvironment(self):
        raise NotImplementedError

    def switchEnvironment(self, envState, setCallback=True):
        raise NotImplementedError

    def switchDayNightMode(self, envState):
        raise NotImplementedError

    def resolveDayNightMode(self, envState):
        raise NotImplementedError

    def getTimeAngle(self):
        raise NotImplementedError


class INewYearCurrencyController(IGameController):
    onCurrencyUpdated = None
    onVisibleCurrenciesChanged = None

    @property
    def getCurrencies(self):
        raise NotImplementedError

    @property
    def getGiftMachineTokenCount(self):
        raise NotImplementedError

    @property
    def getMandarinTokenCount(self):
        raise NotImplementedError

    @property
    def getGoldCount(self):
        raise NotImplementedError

    def getCurrencyCount(self, currency):
        raise NotImplementedError

    def getCurrencyClickHandler(self, currency):
        raise NotImplementedError

    def setVisibleCurrencies(self, currencies=None):
        raise NotImplementedError


class INewYearTamagotchiController(IGameController):

    @property
    def isEntObtained(self):
        raise NotImplementedError

    @property
    def isPetVisible(self):
        raise NotImplementedError


class IOldManController(IGameController):

    def tryShowOldMan(self):
        raise NotImplementedError

    def showOldMan(self):
        raise NotImplementedError

    def getSoundEvent(self):
        raise NotImplementedError


class ITamagotchiWebRequester(object):
    __slots__ = ()

    def requestPlayerInfo(self):
        raise NotImplementedError

    def requestLeaderboardPage(self, page=0, isUserPage=False):
        raise NotImplementedError

    def requestPlayerStats(self):
        raise NotImplementedError

    def buyItems(self, itemsDict):
        raise NotImplementedError

    def activateItem(self, itemId, count):
        raise NotImplementedError

    def takeGift(self):
        raise NotImplementedError


class ITamagotchiDataProvider(object):
    __slots__ = ('onLeaderBoardUpdated', '_onPlayerInfoUpdated', 'onPlayerStatsUpdated', 'onRaccoonStateUpdated', 'onBonusUpdated', 'onSimulationEnd', 'onItemsActivateRequested', 'onItemsActivated', 'onItemsPurchased', 'onOnboardingChanged', 'onGiftObtained', 'onViewVisibilityChanged', 'onMailRewards', 'onGiftCountUpdated', 'onUpdateTipsRequested', 'onNextSeasonStarted', 'onSeasonEnded', 'onOnboardingSkipped')

    def __init__(self):
        super(ITamagotchiDataProvider, self).__init__()
        self.onLeaderBoardUpdated = None
        self.onPlayerStatsUpdated = None
        self.onRaccoonStateUpdated = None
        self.onBonusUpdated = None
        self.onGiftCountUpdated = None
        self.onSimulationEnd = None
        self.onItemsActivateRequested = None
        self.onItemsActivated = None
        self.onItemsPurchased = None
        self.onOnboardingChanged = None
        self.onOnboardingSkipped = None
        self.onGiftObtained = None
        self.onViewVisibilityChanged = None
        self._onPlayerInfoUpdated = None
        self.onMailRewards = None
        self.onUpdateTipsRequested = None
        self.onNextSeasonStarted = None
        self.onSeasonEnded = None
        return

    @property
    def isValidConfig(self):
        raise NotImplementedError

    @property
    def raccoonState(self):
        raise NotImplementedError

    @raccoonState.setter
    def raccoonState(self, value):
        raise NotImplementedError

    @property
    def leaderboard(self):
        raise NotImplementedError

    @leaderboard.setter
    def leaderboard(self, value):
        raise NotImplementedError

    @property
    def config(self):
        raise NotImplementedError

    @config.setter
    def config(self, value):
        raise NotImplementedError

    @property
    def playerInfo(self):
        raise NotImplementedError

    @playerInfo.setter
    def playerInfo(self, value):
        raise NotImplementedError

    @property
    def initialPlayerInfo(self):
        raise NotImplementedError

    @property
    def isOnboarding(self):
        raise NotImplementedError

    @isOnboarding.setter
    def isOnboarding(self, value):
        raise NotImplementedError

    @property
    def isLeaderboardFinished(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def resetData(self):
        raise NotImplementedError

    def getIndicatorCurrency(self, name):
        raise NotImplementedError

    def getDeb(self):
        raise NotImplementedError

    def getIndicatorDeb(self, name):
        raise NotImplementedError

    def getNeeds(self):
        raise NotImplementedError

    def getIndicatorStateDecayTime(self, name):
        raise NotImplementedError

    def getGiftDelay(self):
        raise NotImplementedError

    def getIndicatorDecayTime(self, name):
        raise NotImplementedError

    def getIndicatorStates(self):
        raise NotImplementedError
