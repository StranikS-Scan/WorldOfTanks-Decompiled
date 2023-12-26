# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_controller.py
import typing
import logging
from collections import namedtuple
import Math
from Event import EventManager, Event
from PlayerEvents import g_playerEvents
from CurrentVehicle import g_currentVehicle
from adisp import adisp_async, adisp_process
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.new_year.navigation import NewYearNavigation
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.gui_items.loot_box import NewYearCategories
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from festivity.base import FestivityQuestsHangarFlag
from items import new_year
from items.components.ny_constants import NY_STATE, TOY_TYPES_BY_OBJECT, CustomizationObjects, CurrentNYConstants
from items.components.ny_constants import YEARS_INFO, YEARS
from items.new_year import getToyMask
from new_year.ny_constants import NewYearSysMessages, SyncDataKeys, NyWidgetTopMenu, DAYS_BETWEEN_FRIEND_TAB_REMINDER
from new_year.ny_currencies_helper import NyCurrenciesHelper
from new_year.ny_customization_objects_helper import CustomizationObjectsHelper
from new_year.ny_level_helper import LevelInfo, getLevelIndexes
from new_year.ny_navigation_helper import NewYearNavigationHelper
from new_year.ny_notifications_helpers import LootBoxNotificationHelper
from new_year.ny_processor import HangToyProcessor
from new_year.ny_requester import FriendNewYearRequester
from new_year.ny_resource_collecting_helper import ResourceCollectingHelper
from new_year.ny_sacks_helper import NYSacksHelper
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController, IFriendServiceController
from skeletons.gui.game_control import IBootcampController, IHeroTankController, IPlatoonController
from account_helpers.AccountSettings import AccountSettings, NY_NARKET_PLACE_PAGE_VISITED, NY_NO_FRIENDS_PAGE_RESET_TIME
from new_year.ny_constants import GuestsQuestsTokens
from new_year.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_marketplace_helper import isCollectionReceived
if typing.TYPE_CHECKING:
    from typing import Optional
    from new_year.ny_requester import NewYearRequester
_HangarFlag = namedtuple('_HangarFlag', 'icon, iconDisabled, flagBackground')
_NY_STATE_TRANSITION_SYS_MESSAGES = {(NY_STATE.IN_PROGRESS, NY_STATE.SUSPENDED): NewYearSysMessages(R.strings.ny.notification.suspend(), NotificationPriorityLevel.HIGH, SystemMessages.SM_TYPE.Warning),
 (NY_STATE.SUSPENDED, NY_STATE.IN_PROGRESS): NewYearSysMessages(R.strings.ny.notification.resume(), NotificationPriorityLevel.HIGH, SystemMessages.SM_TYPE.Warning),
 (NY_STATE.FINISHED,): NewYearSysMessages(R.strings.ny.notification.finish(), NotificationPriorityLevel.MEDIUM, SystemMessages.SM_TYPE.Information),
 (NY_STATE.IN_PROGRESS, NY_STATE.FINISHED): NewYearSysMessages(R.strings.ny.notification.finish(), NotificationPriorityLevel.MEDIUM, SystemMessages.SM_TYPE.Information)}
_NY_STATE_SYS_MESSAGES = {NY_STATE.SUSPENDED: _NY_STATE_TRANSITION_SYS_MESSAGES[NY_STATE.IN_PROGRESS, NY_STATE.SUSPENDED],
 NY_STATE.FINISHED: _NY_STATE_TRANSITION_SYS_MESSAGES[NY_STATE.IN_PROGRESS, NY_STATE.FINISHED]}
_logger = logging.getLogger(__name__)

def _getState(state):
    return NY_STATE.FINISHED if state not in NY_STATE.ALL else state


class NewYearController(INewYearController, IGlobalListener):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _bootcampController = dependency.descriptor(IBootcampController)
    _systemMessages = dependency.descriptor(ISystemMessages)
    _friendService = dependency.descriptor(IFriendServiceController)
    __heroTankController = dependency.descriptor(IHeroTankController)
    __platoonController = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(NewYearController, self).__init__()
        self.__commandProcessor = None
        self.__state = None
        self.__notLoggedIn = True
        self.__levelsInfo = None
        self.__em = EventManager()
        self.onDataUpdated = Event(self.__em)
        self.onStateChanged = Event(self.__em)
        self.onWidgetLevelUpAnimationEnd = Event(self.__em)
        self.onUpdateSlot = Event(self.__em)
        self.onBoughtToy = Event(self.__em)
        self.onNyViewVisibilityChange = Event(self.__em)
        self.__notificationHelper = LootBoxNotificationHelper()
        self.__navigationHelper = NewYearNavigationHelper()
        self.__currenciesHelper = NyCurrenciesHelper()
        self.__resourceCollectingHelper = ResourceCollectingHelper()
        self.__customizationObjectsHelper = CustomizationObjectsHelper()
        self.__callbackDelayer = CallbackDelayer()
        self.__friendRequester = FriendNewYearRequester()
        self.__sacksHelper = NYSacksHelper()
        self.__storedUserVehicle = None
        self.__isNyViewShown = False
        self.__isSacksMarkerShown = True
        self.__resourceTypeFrom = u''
        self.__resourceTypeTo = u''
        self.__isResourcesFinishVisited = False
        self.__friendsResourcesFinishVisited = {}
        self.__hangToyEffectEnabled = False
        self.__savedBoxButtonConfig = {NewYearCategories.NEWYEAR: 0,
         NewYearCategories.CHRISTMAS: 0,
         NewYearCategories.ORIENTAL: 0,
         NewYearCategories.FAIRYTALE: 0}
        self.__piggyTokensCount = 0
        self.__isPiggyOpenAnimationTriggered = False
        self.__marketPlaceCollection = []
        return

    def init(self):
        self.__commandProcessor = dependency.instance(IFestivityFactory).getProcessor()

    def fini(self):
        self.__commandProcessor = None
        self.__em.clear()
        return

    def onLobbyInited(self, event):
        if self._bootcampController.isInBootcamp():
            return
        self.__notificationHelper.onLobbyInited()
        self.__navigationHelper.onLobbyInited()
        self.__currenciesHelper.onLobbyInited()
        self.__resourceCollectingHelper.onLobbyInited()
        self.__customizationObjectsHelper.onLobbyInited()
        self.__sacksHelper.onLobbyInited()
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self._eventsCache.onSyncCompleted += self.__onEventsDataChanged
        self._friendService.onFriendHangarEnter += self.__onFriendHangarEnter
        self._friendService.onFriendHangarExit += self.__onFriendHangarExit
        NewYearNavigation.onObjectStateChanged += self.__onObjectUpdate
        NewYearNavigation.onSwitchView += self.__onSwitchView
        self.__eventsDataUpdate()
        self.startGlobalListening()
        if self.isSuspended() and self.__notLoggedIn:
            self.showStateMessage()
        self.__notLoggedIn = False
        self.__marketPlaceCollection = [ (i, YEARS.getYearStrFromYearNum(year)) for i, year in enumerate(YEARS_INFO.prevYearsDecreasingIter()) ]

    def onAvatarBecomePlayer(self):
        self.__notificationHelper.onAvatarBecomePlayer()
        self.__clear()

    def onDisconnected(self):
        self.__notificationHelper.onDisconnected()
        self.__clear()
        self.__notLoggedIn = True
        self.__isSacksMarkerShown = True
        self.__state = None
        self.__resourceTypeFrom = u''
        self.__savedBoxButtonConfig = {NewYearCategories.NEWYEAR: 0,
         NewYearCategories.CHRISTMAS: 0,
         NewYearCategories.ORIENTAL: 0,
         NewYearCategories.FAIRYTALE: 0}
        self.__piggyTokensCount = 0
        self.__isPiggyOpenAnimationTriggered = False
        self.__resourceTypeTo = u''
        self.__isResourcesFinishVisited = False
        self.__friendsResourcesFinishVisited = {}
        return

    def isEnabled(self):
        return self.__state == NY_STATE.IN_PROGRESS and not self._bootcampController.isInBootcamp()

    def getHangarQuestsFlagData(self):
        return FestivityQuestsHangarFlag(None, None, None)

    def isFinished(self):
        return self.__state == NY_STATE.FINISHED and not self._bootcampController.isInBootcamp()

    def isSuspended(self):
        return self.__state == NY_STATE.SUSPENDED and not self._bootcampController.isInBootcamp()

    def isMaxAtmosphereLevel(self):
        return self.requester.getMaxLevel() == new_year.MAX_ATMOSPHERE_LVL

    def isSacksMarkerShown(self):
        return self.__isSacksMarkerShown

    def setIsSacksMarker(self, state):
        self.__isSacksMarkerShown = state

    def getHangarEdgeColor(self):
        return Math.Vector4(0.212, 0.843, 1, 1)

    @staticmethod
    def getToyDescr(toyID):
        return new_year.g_cache.toys.get(toyID)

    def getAllToysByType(self, toyType):
        return [ toy for toy in new_year.g_cache.toys.itervalues() if toy.type == toyType ]

    def getToysBySlot(self, slotID):
        toys = self.__getCurrentToys()
        return toys[slotID] if slotID in toys else {}

    def getAllCollectedToysId(self):
        collectedToys = set()
        toyCollection = self._itemsCache.items.festivity.getToyCollection()
        for toyID, toyDescr in new_year.g_cache.toys.iteritems():
            bytePos, mask = getToyMask(toyID, toyDescr.collection)
            if toyCollection[bytePos] & mask:
                collectedToys.add(toyID)

        return collectedToys

    @adisp_async
    @adisp_process
    def hangToy(self, toyID, slotID, callback=None):
        result = yield HangToyProcessor(toyID, slotID).request()
        self.__hangToyEffectEnabled = True
        if result.success:
            self.onUpdateSlot(slotID, toyID)
        else:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if callback is not None:
            callback(result)
        return

    def getLevel(self, level):
        if self.__levelsInfo is None:
            self.__createLevels()
        return self.__levelsInfo[level]

    def checkForNewToys(self):
        for type in CustomizationObjects.ALL:
            if self.checkForNewToysByType(type):
                return True

        return False

    def checkForNewToysInSlot(self, slot):
        toyInSlots = self.getToysBySlot(slot)
        for toyID in toyInSlots:
            if toyInSlots[toyID].getUnseenCount() > 0:
                return True

        return False

    def checkForNewToysByType(self, objectType):
        toysType = TOY_TYPES_BY_OBJECT.get(objectType)
        slots = [ slot for slot in self.getSlotDescrs() if slot.type in toysType ]
        for slot in slots:
            if self.checkForNewToysInSlot(slot.id):
                return True

        return False

    def showStateMessage(self):
        msg = _NY_STATE_SYS_MESSAGES.get(self.__state)
        if msg is not None:
            SystemMessages.pushMessage(backport.text(msg.keyText), type=msg.type, priority=msg.priority, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})
        return

    def sendSeenToys(self, slotID):
        self.__commandProcessor.sendSeen(slotID)

    def chooseXPBonus(self, choiceID):
        self.__commandProcessor.chooseXPBonus(choiceID)

    def convertResources(self, initialResourceID, receivedResourceID, initialValue, callback=None):
        self.__commandProcessor.convertResources(initialResourceID, receivedResourceID, initialValue, callback)

    def sendSeenToysInCollection(self, toyIDs):
        result = []
        for toyID in toyIDs:
            result.extend((toyID, 0))

        self.__commandProcessor.seenInCollection(result)

    def prepareNotifications(self, tokens):
        self.__notificationHelper.prepareNotifications(tokens)

    def getNumberOfSlotsByType(self, slotType):
        return len([ slot for slot in self.getSlotDescrs() if slot.type == slotType ])

    def setWidgetLevelUpAnimationEnd(self):
        self.onWidgetLevelUpAnimationEnd()

    @staticmethod
    def getSlotDescrs():
        return tuple(new_year.g_cache.slots)

    @property
    def currencies(self):
        return self.__currenciesHelper

    @property
    def customizationObjects(self):
        return self.__customizationObjectsHelper

    @property
    def resourceCollecting(self):
        return self.__resourceCollectingHelper

    @property
    def requester(self):
        return self.__friendRequester if self._friendService.isInFriendHangar else self._itemsCache.items.festivity

    @property
    def sacksHelper(self):
        return self.__sacksHelper

    def getHangToyEffectEnabled(self):
        return self.__hangToyEffectEnabled

    def setHangToyEffectEnabled(self, value):
        self.__hangToyEffectEnabled = value

    def getHangarNameMask(self):
        return self.requester.getHangarNameMask()

    def isNyViewShown(self):
        return self.__isNyViewShown

    def resetNYDailyLimits(self):
        self.__commandProcessor.resetNYDailyLimits()

    def addToys(self, toysDict=None):
        self.__commandProcessor.addToys(toysDict)

    def addResource(self, type_, count=1000):
        self.__commandProcessor.addResource(count, type_)

    def addToysSet(self, settingId=''):
        if settingId == '' or settingId not in YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME:
            return
        toysDict = {}
        for slot in new_year.g_cache.slots:
            toys = [ toy for toy in new_year.g_cache.toys.itervalues() if toy.type == slot.type and toy.setting == settingId ]
            if toys:
                toysDict[slot.id] = {}
                for toy in toys:
                    toysDict[slot.id][toy.id] = 1

        self.__commandProcessor.addToys(toysDict)

    def isTokenReceived(self, token):
        return self.requester.isTokenReceived(token)

    def isDogTokenReceived(self):
        return self.isTokenReceived(GuestsQuestsTokens.TOKEN_DOG)

    def isCatTokenReceived(self):
        return self.isTokenReceived(GuestsQuestsTokens.TOKEN_CAT)

    def getTokenCount(self, token):
        return self.requester.getTokenCount(token)

    def getFirstNonReceivedMarketPlaceCollectionData(self):
        collection = self.__marketPlaceCollection
        res = [ (i, year) for i, year in collection if not isCollectionReceived(year) ]
        return (res if res else collection)[0]

    def getInstalledToyInSlot(self, slotID):
        slotsData = self.requester.getSlotsData()
        return slotsData[slotID]

    def setResourceTypeFrom(self, resource):
        self.__resourceTypeFrom = resource

    def getResourceTypeFrom(self):
        return self.__resourceTypeFrom

    def setResourceTypeTo(self, resource):
        self.__resourceTypeTo = resource

    def getResourceTypeTo(self):
        return self.__resourceTypeTo

    def setSavedBoxesButton(self, boxCategory, buttonKey):
        self.__savedBoxButtonConfig[boxCategory] = buttonKey

    def getSavedBoxesButton(self, boxCategory):
        return int(self.__savedBoxButtonConfig.get(boxCategory, 0))

    def getPiggyTokensCount(self):
        return int(self.__piggyTokensCount)

    def setPiggyTokensCount(self, amount):
        self.__piggyTokensCount = amount

    def getIsPiggyOpenAnimationTriggered(self):
        return bool(self.__isPiggyOpenAnimationTriggered)

    def setIsPiggyOpenAnimationTriggered(self, isTriggered):
        self.__isPiggyOpenAnimationTriggered = isTriggered

    def setIsResourcesFinishVisited(self, isVisited):
        self.__isResourcesFinishVisited = isVisited

    def getIsResourcesFinishVisited(self):
        return self.__isResourcesFinishVisited

    def setFriendsResourcesFinishVisited(self, spaId):
        self.__friendsResourcesFinishVisited[spaId] = True

    def getFriendsResourcesFinishVisited(self, spaId):
        return self.__friendsResourcesFinishVisited.get(spaId, False)

    def __onClientUpdated(self, diff, _):
        festivityKey = self._itemsCache.items.festivity.dataKey
        if festivityKey in diff:
            if SyncDataKeys.POINTS in diff.get(CurrentNYConstants.PDATA_KEY, {}):
                if NewYearAtmospherePresenter.getLevel() == new_year.MAX_ATMOSPHERE_LVL:
                    AccountSettings.setUIFlag(NY_NARKET_PLACE_PAGE_VISITED, False)
            keys = diff[festivityKey].keys()
            self.onDataUpdated(keys, diff)

    def __onEventsDataChanged(self):
        self.__eventsDataUpdate()
        if self.__levelsInfo is not None:
            for levelInfo in self.__levelsInfo.itervalues():
                levelInfo.updateBonuses()

        return

    def __eventsDataUpdate(self):
        state = self.__getEventState()
        self.__setState(state)

    def __getEventState(self):
        state = None
        for action in self._eventsCache.getActions().itervalues():
            if 'EventState' in action.getModifiersDict():
                state = action.getModifiersDict()['EventState'].getState()

        return state

    def __setState(self, state):
        state = _getState(state)
        if self.__state != state:
            self.__showSystemMessage(state)
            self.__state = state
            self.onStateChanged()

    def __showSystemMessage(self, newState):
        msg = _NY_STATE_TRANSITION_SYS_MESSAGES.get((self.__state, newState))
        if msg is not None:
            SystemMessages.pushMessage(backport.text(msg.keyText), priority=msg.priority, type=msg.type)
        return

    def hangToys(self):
        for slotID, toyID in enumerate(self.requester.getSlotsData()):
            self.onUpdateSlot(slotID, toyID)

    def __createLevels(self):
        self.__levelsInfo = {}
        levelRewardsByID = new_year.g_cache.levelRewardsByID
        quests = self._eventsCache.getQuestsByIDs(levelRewardsByID.itervalues())
        for level in getLevelIndexes():
            self.__levelsInfo[level] = LevelInfo(level, quests[levelRewardsByID[level]])

    def __clear(self):
        self.__levelsInfo = None
        self.__resourceCollectingHelper.clear()
        self.__navigationHelper.clear()
        self.stopGlobalListening()
        self.__storedUserVehicle = None
        self.__marketPlaceCollection = []
        self.__currenciesHelper.clear()
        self.__customizationObjectsHelper.clear()
        self.__callbackDelayer.clearCallbacks()
        self.__sacksHelper.clear()
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self._eventsCache.onSyncCompleted -= self.__onEventsDataChanged
        self._friendService.onFriendHangarEnter -= self.__onFriendHangarEnter
        self._friendService.onFriendHangarExit -= self.__onFriendHangarExit
        NewYearNavigation.onObjectStateChanged -= self.__onObjectUpdate
        NewYearNavigation.onSwitchView -= self.__onSwitchView
        return

    def __getCurrentToys(self):
        return self.requester.getToys()

    def __onFriendHangarEnter(self, *args):
        self.__updateFriendHangar(True)
        self.__storePlayerState()
        self.__platoonController.onPlatoonTankVisualizationChanged(False)
        self.__heroTankController.setEnabled(False)

    def __onFriendHangarExit(self, *args):
        self.__updateFriendHangar(False)
        self.__restorePlayerState()
        self.__platoonController.onPlatoonTankVisualizationChanged(True)
        self.__heroTankController.setEnabled(True)
        self.__storedUserVehicle = None
        return

    def __onObjectUpdate(self):
        isNyViewShown = NewYearNavigation.getCurrentObject() is not None
        if self.__isNyViewShown != isNyViewShown:
            self.__isNyViewShown = isNyViewShown
            self.onNyViewVisibilityChange(self.__isNyViewShown)
        return

    def __storePlayerState(self):
        self.__storedUserVehicle = g_currentVehicle.invID
        g_currentVehicle.selectNoVehicle()

    def __restorePlayerState(self):
        if self.__storedUserVehicle:
            g_currentVehicle.selectVehicle(self.__storedUserVehicle)

    def __updateFriendHangar(self, isInFriend):
        self.__hangToyEffectEnabled = False
        self.hangToys()

    @staticmethod
    def __onSwitchView(ctx):
        if ctx.menuName == NyWidgetTopMenu.FRIENDS:
            lastSeenTime = AccountSettings.getUIFlag(NY_NO_FRIENDS_PAGE_RESET_TIME)
            currentTime = time_utils.getServerUTCTime()
            resetTimeDelta = DAYS_BETWEEN_FRIEND_TAB_REMINDER * time_utils.ONE_DAY
            if currentTime >= lastSeenTime + resetTimeDelta:
                AccountSettings.setUIFlag(NY_NO_FRIENDS_PAGE_RESET_TIME, currentTime)
