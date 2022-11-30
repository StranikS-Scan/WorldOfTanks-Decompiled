# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/new_year.py
import typing
import wg_async
from adisp import adisp_async
from skeletons.gui.game_control import IFestivityController, IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from gui.server_events.event_items import TokenQuest, CelebrityQuest, CelebrityTokenQuest
    from Math import Vector3, Vector4
    from new_year.ny_requester import _NewYearToy, FriendNewYearRequester, NewYearRequester
    from new_year.ny_resource_collecting_helper import ResourceCollectingHelper
    from new_year.ny_currencies_helper import NyCurrenciesHelper
    from new_year.ny_customization_objects_helper import CustomizationObjectsHelper
    from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_view_model import MachineState
    from items.collectibles import ToyDescriptor
    from typing import Optional

class INewYearController(IFestivityController):
    onDataUpdated = None
    onWidgetLevelUpAnimationEnd = None
    onBoughtToy = None
    onHangToy = None
    onUpdateSlot = None
    onSetHangToyEffectEnabled = None
    onNyViewVisibilityChange = None

    def isEnabled(self):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isSuspended(self):
        raise NotImplementedError

    def isMaxAtmosphereLevel(self):
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

    def getAllToysByType(self, slotID):
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

    def setWidgetLevelUpAnimationEnd(self):
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

    def getHangarNameMask(self):
        raise NotImplementedError

    def isNyViewShown(self):
        raise NotImplementedError

    @property
    def requester(self):
        raise NotImplementedError

    def isTokenReceived(self, token):
        raise NotImplementedError

    def getTokenCount(self, token):
        raise NotImplementedError

    def getFirstNonReceivedMarketPlaceCollectionData(self):
        raise NotImplementedError


class INewYearTutorialController(IGameController):

    def startTutorial(self):
        raise NotImplementedError

    def markNameSelected(self):
        raise NotImplementedError

    def overlayStateChanged(self):
        raise NotImplementedError

    def inProgress(self):
        raise NotImplementedError


class IGiftMachineController(IGameController):
    onBuyStateChanged = None
    onRedButtonStateChanged = None
    onRedButtonPress = None
    onSkipAnimStateChanged = None

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


class IFriendServiceController(IGameController):
    onFriendHangarEnter = None
    onFriendHangarExit = None
    onFriendServiceStateChanged = None

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

    @wg_async.wg_async
    def updateFriendList(self):
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


class IJukeboxController(IGameController):
    onPlaylistSelected = None
    onTrackSuspended = None
    onHighlightEnable = None
    onHighlighted = None
    onFaded = None

    def onAnimatorEvent(self, name):
        raise NotImplementedError

    def handleJukeboxClick(self, side):
        raise NotImplementedError

    def handleJukeboxHighlight(self, side, isHighlighed):
        raise NotImplementedError

    def setJukeboxPosition(self, position):
        raise NotImplementedError


class ICelebritySceneController(IGameController):
    onQuestsUpdated = None

    @property
    def isChallengeVisited(self):
        raise NotImplementedError

    @property
    def isWelcomeAnimationViewed(self):
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
    def hasNewCompletedAddQuests(self):
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
    def completedAddQuestsMask(self):
        raise NotImplementedError

    @property
    def questsCount(self):
        raise NotImplementedError

    @property
    def completedQuestsCount(self):
        raise NotImplementedError

    @property
    def completedAddQuestsCount(self):
        raise NotImplementedError

    def onEnterChallenge(self):
        raise NotImplementedError

    def onExitChallenge(self):
        raise NotImplementedError


class ICelebrityController(IGameController):
    onCelebActionTokensUpdated = None
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
