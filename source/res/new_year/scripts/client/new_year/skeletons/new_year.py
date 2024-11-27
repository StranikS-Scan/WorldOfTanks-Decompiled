# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/skeletons/new_year.py
import typing
from adisp import adisp_async
from new_year_common.items.components.ny_constants import RANDOM_VALUE, FillerState
from skeletons.gui.game_control import IFestivityController, IGameController, IFestivityTutorialController
if typing.TYPE_CHECKING:
    from typing import Callable, Optional

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

    def isEnabled(self):
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

    def getActiveMultiplier(self):
        raise NotImplementedError

    def getActiveCollectionsBonus(self):
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

    def isWidgetVisible(self, prbState, alias=None):
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


class INewYearCraftMachineController(IGameController):
    selectedToyTypeIdx = RANDOM_VALUE
    selectedToySettingIdx = 0
    selectedToyRankIdx = 0
    fillerState = None

    @property
    def fillerShardsCost(self):
        raise NotImplementedError

    @property
    def isConnected(self):
        raise NotImplementedError

    def getSelectedToyType(self):
        raise NotImplementedError

    def getToyCategoryType(self):
        raise NotImplementedError

    def getRegularSelectedToyType(self):
        raise NotImplementedError

    def setSettings(self, toyTypeID=RANDOM_VALUE, settingID=RANDOM_VALUE, rank=RANDOM_VALUE, fillerState=FillerState.INACTIVE):
        raise NotImplementedError

    def calculateSelectedToyCraftCost(self):
        raise NotImplementedError

    def calculateToyCraftCost(self, toyTypeIdx, toySettingIdx, toyRankIdx, fillerState):
        raise NotImplementedError


class INewYearTutorialController(IFestivityTutorialController):
    onIntroComplete = None

    def shouldStartIntro(self):
        raise NotImplementedError

    @property
    def isActive(self):
        raise NotImplementedError

    def tryStartIntro(self):
        raise NotImplementedError


class INewYearSurpriseMachine(IGameController):
    onStateUpdate = None
    onMachineButtonPress = None
    onUpdateApplyCoin = None
    onMachineButtonHovered = None

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

    def setState(self, state):
        raise NotImplementedError

    def setViewState(self, state):
        raise NotImplementedError

    def updateSurpriseMachineBusyStatus(self, isBusy):
        raise NotImplementedError


class INewYearRaccoonController(IGameController):
    onViewExit = None

    def showFade(self, callback=None):
        raise NotImplementedError

    def hideFade(self):
        raise NotImplementedError


class INewYearBubbleNavigationController(IGameController):
    onUpdateBubble = None

    @classmethod
    def checkIfHasNavigationBubble(cls, navigationName):
        raise NotImplementedError
