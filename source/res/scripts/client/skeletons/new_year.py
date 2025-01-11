# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/new_year.py
import typing
import wg_async
from adisp import adisp_async
from skeletons.gui.game_control import IFestivityController, IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_model import NySidebarModel
    from gui.server_events.event_items import TokenQuest, CelebrityQuest, CelebrityTokenQuest
    from Math import Vector4
    from new_year.ny_requester import _NewYearToy, FriendNewYearRequester, NewYearRequester
    from new_year.ny_resource_collecting_helper import ResourceCollectingHelper
    from new_year.ny_currencies_helper import NyCurrenciesHelper
    from new_year.ny_customization_objects_helper import CustomizationObjectsHelper
    from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_view_model import MachineState
    from new_year.ny_trigger_hints import TriggerHintsStates
    from new_year.ny_sacks_helper import NYSacksHelper
    from items.collectibles import ToyDescriptor
    from items.components.ny_components import SlotDescriptor
    from typing import Optional
    from ny_common.GuestsQuestsConfig import GuestQuest

class INewYearController(IFestivityController):
    onDataUpdated = None
    onWidgetLevelUpAnimationEnd = None
    onBoughtToy = None
    onUpdateSlots = None
    onSacksMarkerShow = None
    onNyViewVisibilityChange = None
    onCustomizationObjectLevelUp = None

    def isEnabled(self):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isSuspended(self):
        raise NotImplementedError

    def isMaxAtmosphereLevel(self):
        raise NotImplementedError

    def isSacksMarkerShown(self):
        raise NotImplementedError

    def getHangarEdgeColor(self):
        raise NotImplementedError

    @staticmethod
    def getSlotDescrs():
        raise NotImplementedError

    @staticmethod
    def getToyDescr(toyID):
        raise NotImplementedError

    def chooseXPBonus(self, choiceID):
        raise NotImplementedError

    def convertResources(self, initialResourceID, receivedResourceID, initialValue, callback=None):
        raise NotImplementedError

    def getToysBySlot(self, slotID):
        raise NotImplementedError

    def getAllCollectedToysId(self):
        raise NotImplementedError

    @adisp_async
    def hangToy(self, toyID, slotID, callback=None):
        raise NotImplementedError

    def getLevel(self, level):
        raise NotImplementedError

    def checkForNewToys(self):
        raise NotImplementedError

    def checkForNewToysInSlot(self, slot):
        raise NotImplementedError

    def checkForNewToysByType(self, objectType):
        raise NotImplementedError

    def showStateMessage(self):
        raise NotImplementedError

    def sendSeenToys(self, slotID):
        raise NotImplementedError

    def sendSeenToysInCollection(self, toyIDs):
        raise NotImplementedError

    def prepareNotifications(self, tokens):
        raise NotImplementedError

    def getNumberOfSlotsByType(self, slotType):
        raise NotImplementedError

    def setWidgetLevelUpAnimationEnd(self):
        raise NotImplementedError

    def setCustomizationObjectLevelUp(self):
        raise NotImplementedError

    def setIsSacksMarker(self, state):
        raise NotImplementedError

    @property
    def currencies(self):
        raise NotImplementedError

    @property
    def customizationObjects(self):
        raise NotImplementedError

    @property
    def resourceCollecting(self):
        raise NotImplementedError

    def getHangToyEffectEnabled(self):
        raise NotImplementedError

    def setHangToyEffectEnabled(self, value):
        raise NotImplementedError

    def getHangarNameMask(self):
        raise NotImplementedError

    def isNyViewShown(self):
        raise NotImplementedError

    @property
    def requester(self):
        raise NotImplementedError

    @property
    def sacksHelper(self):
        raise NotImplementedError

    def isTokenReceived(self, token):
        raise NotImplementedError

    def isDogTokenReceived(self):
        raise NotImplementedError

    def isCatTokenReceived(self):
        raise NotImplementedError

    def getTokenCount(self, token):
        raise NotImplementedError

    def getFirstNonReceivedMarketPlaceCollectionData(self):
        raise NotImplementedError

    def getInstalledToyInSlot(self, slotID):
        raise NotImplementedError

    def setResourceTypeFrom(self, resource):
        raise NotImplementedError

    def getResourceTypeFrom(self):
        raise NotImplementedError

    def setResourceTypeTo(self, resource):
        raise NotImplementedError

    def getResourceTypeTo(self):
        raise NotImplementedError

    def setSavedBoxesButton(self, boxCategory, buttonKey):
        raise NotImplementedError

    def getSavedBoxesButton(self, boxCategory):
        raise NotImplementedError

    def setPiggyTokensCount(self, amount):
        raise NotImplementedError

    def getPiggyTokensCount(self):
        raise NotImplementedError

    def setIsPiggyOpenAnimationTriggered(self, isTriggered):
        raise NotImplementedError

    def getIsPiggyOpenAnimationTriggered(self):
        raise NotImplementedError

    def setIsResourcesFinishVisited(self, resource):
        raise NotImplementedError

    def getIsResourcesFinishVisited(self):
        raise NotImplementedError

    def setFriendsResourcesFinishVisited(self, spaId):
        raise NotImplementedError

    def getFriendsResourcesFinishVisited(self, spaId):
        raise NotImplementedError


class INewYearTutorialController(IGameController):

    def markNameSelected(self):
        raise NotImplementedError

    def startIntro(self, callback=None):
        raise NotImplementedError

    def inProgress(self):
        raise NotImplementedError

    def resetCameraToTank(self):
        raise NotImplementedError

    def moveCameraToTop(self):
        raise NotImplementedError


class INewYearTriggerHintsController(IGameController):
    onStateChanged = None

    @property
    def triggerHintsState(self):
        raise NotImplementedError

    def setActiveSidebarTabs(self, model, menuName, tabName):
        raise NotImplementedError

    def getActiveMenuTabs(self, tabName):
        raise NotImplementedError

    def hide(self):
        raise NotImplementedError

    def checkForGuestARequirements(self, withoutResourceCheck=False):
        raise NotImplementedError

    def checkForTournamentRequirements(self, withoutHintSkippedCheck=False):
        raise NotImplementedError


class IGiftMachineController(IGameController):
    onBuyStateChanged = None
    onRedButtonStateChanged = None
    onRedButtonPress = None
    onSkipAnimStateChanged = None
    onLootListInfoUpdated = None
    onLootListInfoWindowStateChanged = None
    onGoToBuyTokens = None

    @property
    def isBuyingCoinsAvailable(self):
        raise NotImplementedError

    @property
    def isBuyCoinVisited(self):
        raise NotImplementedError

    @property
    def isEnable(self):
        raise NotImplementedError

    @property
    def isGiftMachineBusy(self):
        raise NotImplementedError

    @property
    def machineState(self):
        raise NotImplementedError

    @property
    def canApplyCoin(self):
        raise NotImplementedError

    @property
    def canSkipAnim(self):
        raise NotImplementedError

    @property
    def canRedButtonPress(self):
        raise NotImplementedError

    def updateGiftMachineBusyStatus(self, isBusy):
        raise NotImplementedError

    def setInRequestState(self, isInRequest):
        raise NotImplementedError

    def setMachineState(self, state):
        raise NotImplementedError

    def goToBuyState(self):
        raise NotImplementedError

    def getLootListInfo(self):
        raise NotImplementedError


class IFriendServiceController(IGameController):
    onFriendHangarEnter = None
    onFriendHangarExit = None
    onFriendServiceStateChanged = None
    onBestFriendsUpdated = None
    onSwitchFriendCollectingState = None

    @property
    def isInFriendHangar(self):
        raise NotImplementedError

    @property
    def friendHangarSpaId(self):
        raise NotImplementedError

    @property
    def isServiceEnabled(self):
        raise NotImplementedError

    @property
    def friendList(self):
        raise NotImplementedError

    @property
    def maxBestFriendsCount(self):
        raise NotImplementedError

    @property
    def bestFriendList(self):
        raise NotImplementedError

    @wg_async.wg_async
    def enterFriendHangar(self, spaId):
        raise NotImplementedError

    def leaveFriendHangar(self):
        raise NotImplementedError

    def preLeaveFriendHangar(self):
        raise NotImplementedError

    def getBestFriendsResourceData(self):
        raise NotImplementedError

    @wg_async.wg_async
    def updateFriendList(self):
        raise NotImplementedError

    @property
    def hasBeenUpdatedOnce(self):
        raise NotImplementedError

    def getFriendState(self):
        raise NotImplementedError

    def getFriendCollectingCooldownTime(self):
        raise NotImplementedError

    def getFriendTokens(self):
        raise NotImplementedError

    def addBestFriend(self, spaId):
        raise NotImplementedError

    def deleteBestFriend(self, spaId):
        raise NotImplementedError

    def collectFriendResources(self):
        raise NotImplementedError

    def getFriendName(self, spaId):
        raise NotImplementedError

    def isFriendOnline(self, spaId):
        raise NotImplementedError


class ICelebritySceneController(IGameController):
    onQuestsUpdated = None

    @property
    def isChallengeVisited(self):
        raise NotImplementedError

    @property
    def isInChallengeView(self):
        raise NotImplementedError

    @property
    def isChallengeCompleted(self):
        raise NotImplementedError

    @property
    def isAllMainQuestsCompleted(self):
        raise NotImplementedError

    @property
    def hasNewCompletedQuests(self):
        raise NotImplementedError

    @property
    def quests(self):
        raise NotImplementedError

    @property
    def tokens(self):
        raise NotImplementedError

    @property
    def marathonQuests(self):
        raise NotImplementedError

    @property
    def completedDayQuestsMask(self):
        raise NotImplementedError

    @property
    def completedAdvQuestsMask(self):
        raise NotImplementedError

    @property
    def questsCount(self):
        raise NotImplementedError

    @property
    def allQuestsCount(self):
        raise NotImplementedError

    @property
    def completedQuestsCount(self):
        raise NotImplementedError

    @property
    def completedAdvQuestsCount(self):
        raise NotImplementedError

    @property
    def curActiveAdvCount(self):
        raise NotImplementedError

    def onEnterChallenge(self):
        raise NotImplementedError

    def onExitChallenge(self):
        raise NotImplementedError


class ICelebrityController(IGameController):
    onCelebActionTokenUpdated = None
    onCelebCompletedTokensUpdated = None

    def getAllTokens(self, guestNames=None, actionTypes=None):
        raise NotImplementedError

    def getAllReceivedTokens(self, guestNames=None, actionTypes=None):
        raise NotImplementedError

    def getCompletedGuestQuestsCount(self, guestName):
        raise NotImplementedError

    def isGuestQuestsCompletedFully(self, guestNames):
        raise NotImplementedError

    def isGuestQuestCompleted(self, guestQuest):
        raise NotImplementedError

    def doActionByCelebActionToken(self, tokenID):
        raise NotImplementedError
