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
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from items import new_year
from items.components.ny_constants import NY_STATE, TOY_TYPES_BY_OBJECT, CustomizationObjects
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from items.components.ny_constants import YEARS_INFO, YEARS
from items.new_year import getToyMask
from new_year import ny_resource_collecting_helper as ny_res_helper
from new_year.ny_constants import NewYearSysMessages, SyncDataKeys
from new_year.ny_currencies_helper import NyCurrenciesHelper
from new_year.ny_customization_objects_helper import CustomizationObjectsHelper
from new_year.ny_level_helper import LevelInfo, getLevelIndexes
from new_year.ny_navigation_helper import NewYearNavigationHelper
from new_year.ny_notifications_helpers import LootBoxNotificationHelper
from new_year.ny_processor import HangToyProcessor
from new_year.ny_requester import FriendNewYearRequester
from new_year.ny_resource_collecting_helper import ResourceCollectingHelper
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController, IFriendServiceController
from skeletons.gui.game_control import IBootcampController, IBattleRoyaleController, IHeroTankController, IPlatoonController
from account_helpers.AccountSettings import AccountSettings, NY_NARKET_PLACE_PAGE_VISITED
from new_year.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_marketplace_helper import isCollectionReceived
if typing.TYPE_CHECKING:
    from typing import Optional
    from new_year.ny_requester import NewYearRequester
_HangarFlag = namedtuple('_HangarFlag', 'icon, iconDisabled, flagBackground')
_NY_STATE_TRANSITION_SYS_MESSAGES = {(NY_STATE.IN_PROGRESS, NY_STATE.SUSPENDED): NewYearSysMessages(R.strings.ny.notification.suspend(), 'high', SystemMessages.SM_TYPE.Warning),
 (NY_STATE.SUSPENDED, NY_STATE.IN_PROGRESS): NewYearSysMessages(R.strings.ny.notification.resume(), 'high', SystemMessages.SM_TYPE.Warning),
 (NY_STATE.NOT_STARTED, NY_STATE.IN_PROGRESS): NewYearSysMessages(R.strings.ny.notification.start(), 'high', SystemMessages.SM_TYPE.NewYearEventStarted),
 (NY_STATE.FINISHED,): NewYearSysMessages(R.strings.ny.notification.finish(), 'medium', SystemMessages.SM_TYPE.Information),
 (NY_STATE.IN_PROGRESS, NY_STATE.FINISHED): NewYearSysMessages(R.strings.ny.notification.finish(), 'medium', SystemMessages.SM_TYPE.Information),
 (NY_STATE.FINISHED, NY_STATE.IN_PROGRESS): NewYearSysMessages(R.strings.ny.notification.start(), 'high', SystemMessages.SM_TYPE.NewYearEventStarted)}
_NY_STATE_SYS_MESSAGES = {NY_STATE.SUSPENDED: _NY_STATE_TRANSITION_SYS_MESSAGES[NY_STATE.IN_PROGRESS, NY_STATE.SUSPENDED],
 NY_STATE.FINISHED: _NY_STATE_TRANSITION_SYS_MESSAGES[NY_STATE.IN_PROGRESS, NY_STATE.FINISHED]}
_logger = logging.getLogger(__name__)

def _getState(state):
    return NY_STATE.FINISHED if state not in NY_STATE.ALL else state


class NewYearController(INewYearController, IGlobalListener):
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _bootcampController = dependency.descriptor(IBootcampController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _systemMessages = dependency.descriptor(ISystemMessages)
    _battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
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
        self.onSetHangToyEffectEnabled = Event(self.__em)
        self.onBoughtToy = Event(self.__em)
        self.onHangToy = Event(self.__em)
        self.onNyViewVisibilityChange = Event(self.__em)
        self.__spaceUpdated = False
        self.__isBattleRoyaleMode = False
        self.__notificationHelper = LootBoxNotificationHelper()
        self.__navigationHelper = NewYearNavigationHelper()
        self.__currenciesHelper = NyCurrenciesHelper()
        self.__resourceCollectingHelper = ResourceCollectingHelper()
        self.__customizationObjectsHelper = CustomizationObjectsHelper()
        self.__callbackDelayer = CallbackDelayer()
        self.__friendRequester = FriendNewYearRequester()
        self.__storedUserVehicle = None
        self.__isNyViewShown = False
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
        self.__isBattleRoyaleMode = self._battleRoyaleController.isBattleRoyaleMode()
        self.__notificationHelper.onLobbyInited()
        self.__navigationHelper.onLobbyInited()
        self.__currenciesHelper.onLobbyInited()
        self.__resourceCollectingHelper.onLobbyInited()
        self.__customizationObjectsHelper.onLobbyInited()
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self._eventsCache.onSyncCompleted += self.__onEventsDataChanged
        self._hangarSpace.onSpaceCreate += self.__onSpaceCreate
        self._hangarSpace.onSpaceRefresh += self.__onSpaceRefresh
        self._friendService.onFriendHangarEnter += self.__onFriendHangarEnter
        self._friendService.onFriendHangarExit += self.__onFriendHangarExit
        NewYearNavigation.onObjectStateChanged += self.__onObjectUpdate
        self.__eventsDataUpdate()
        self.startGlobalListening()
        if self.isSuspended() and self.__notLoggedIn:
            self.showStateMessage()
        self.__notLoggedIn = False
        years = list(YEARS.ALL)
        years.reverse()
        if YEARS_INFO.CURRENT_YEAR in years:
            years.remove(YEARS_INFO.CURRENT_YEAR)
        self.__marketPlaceCollection = [ (i, YEARS.getYearStrFromYearNum(year)) for i, year in enumerate(years) ]

    def onAvatarBecomePlayer(self):
        self.__notificationHelper.onAvatarBecomePlayer()
        self.__clear()

    def onDisconnected(self):
        self.__notificationHelper.onDisconnected()
        self.__clear()
        self.__notLoggedIn = True

    def isEnabled(self):
        return self.__state == NY_STATE.IN_PROGRESS and not self._bootcampController.isInBootcamp() and not self.__isBattleRoyaleMode

    def isFinished(self):
        return self.__state == NY_STATE.FINISHED and not self._bootcampController.isInBootcamp()

    def isSuspended(self):
        return self.__state == NY_STATE.SUSPENDED and not self._bootcampController.isInBootcamp()

    def isMaxAtmosphereLevel(self):
        return self.requester.getMaxLevel() == new_year.MAX_ATMOSPHERE_LVL

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
        self.onSetHangToyEffectEnabled(True)
        if result.success:
            self.onUpdateSlot(slotID, toyID)
            self.onHangToy(slotID, toyID)
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

    def onPrbEntitySwitched(self):
        isBattleRoyaleMode = self._battleRoyaleController.isBattleRoyaleMode()
        if self.__isBattleRoyaleMode != isBattleRoyaleMode:
            self.__isBattleRoyaleMode = isBattleRoyaleMode
            self.onStateChanged()

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
        return self.__friendRequester if self._friendService.friendHangarSpaId is not None else self._itemsCache.items.festivity

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
        toysDict = {toyID:1 for toyID, toy in new_year.g_cache.toys.iteritems() if toy.setting == settingId}
        self.__commandProcessor.addToys(toysDict)

    def isTokenReceived(self, token):
        return self.requester.isTokenReceived(token)

    def getTokenCount(self, token):
        return self.requester.getTokenCount(token)

    def getFirstNonReceivedMarketPlaceCollectionData(self):
        collection = self.__marketPlaceCollection
        res = [ (i, year) for i, year in collection if not isCollectionReceived(year) ]
        return res[0] if res else (0, YEARS.getYearStrFromYearNum(22))

    def __onClientUpdated(self, diff, _):
        festivityKey = self._itemsCache.items.festivity.dataKey
        if festivityKey in diff:
            if SyncDataKeys.POINTS in diff.get('newYear23', {}):
                if NewYearAtmospherePresenter.getLevel() == new_year.MAX_ATMOSPHERE_LVL:
                    AccountSettings.setUIFlag(NY_NARKET_PLACE_PAGE_VISITED, False)
            keys = diff[festivityKey].keys()
            self.__resourceCollectingHelper.onDataUpdated(keys)
            if SyncDataKeys.RESOURCE_COLLECTING in keys:
                self.__updateResources3DScene()
            self.onDataUpdated(keys, diff)

    def __onEventsDataChanged(self):
        self.__eventsDataUpdate()
        if self.__levelsInfo is not None:
            for levelInfo in self.__levelsInfo.itervalues():
                levelInfo.updateBonuses()

        return

    def __onSpaceCreate(self):
        self.__updateResources3DScene()
        self.__spaceUpdated = False
        self.__hangToys()

    def __onSpaceRefresh(self):
        self.__spaceUpdated = True

    def __eventsDataUpdate(self):
        state = None
        for action in self._eventsCache.getActions().itervalues():
            if 'EventState' in action.getModifiersDict():
                state = action.getModifiersDict()['EventState'].getState()

        self.__setState(state)
        return

    def __setState(self, state):
        state = _getState(state)
        if self.__state != state:
            self.__showSystemMessage(state)
            self.__state = state
            self.onStateChanged()

    def __showSystemMessage(self, newState):
        msg = _NY_STATE_TRANSITION_SYS_MESSAGES.get((self.__state, newState))
        if msg is not None:
            if msg.type == SystemMessages.SM_TYPE.NewYearEventStarted:
                auxData = [msg.type,
                 msg.priority,
                 None,
                 None]
                serviceChannel = self._systemMessages.proto.serviceChannel
                serviceChannel.pushClientMessage(backport.text(msg.keyText), SCH_CLIENT_MSG_TYPE.NY_EVENT_BUTTON_MESSAGE, auxData=auxData)
            else:
                SystemMessages.pushMessage(backport.text(msg.keyText), priority=msg.priority, type=msg.type)
        return

    def __hangToys(self):
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
        self.__spaceUpdated = False
        self.__resourceCollectingHelper.clear()
        self.__navigationHelper.clear()
        self.stopGlobalListening()
        self.__storedUserVehicle = None
        self.__marketPlaceCollection = []
        self.__currenciesHelper.clear()
        self.__customizationObjectsHelper.clear()
        self.__callbackDelayer.clearCallbacks()
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self._eventsCache.onSyncCompleted -= self.__onEventsDataChanged
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self._hangarSpace.onSpaceRefresh -= self.__onSpaceRefresh
        self._friendService.onFriendHangarEnter -= self.__onFriendHangarEnter
        self._friendService.onFriendHangarExit -= self.__onFriendHangarExit
        NewYearNavigation.onObjectStateChanged -= self.__onObjectUpdate
        return

    def __getCurrentToys(self):
        return self.requester.getToys()

    def __updateResources3DScene(self, isInFriend=None):
        if not self.isEnabled():
            return
        if self._friendService.friendHangarSpaId:
            tillTime = self._friendService.getFriendCollectingCooldownTime()
        else:
            tillTime = ny_res_helper.getCollectingCooldownTime()
        if tillTime > 0.0:
            self.__callbackDelayer.delayCallback(tillTime, self.__updateResources3DScene)
            self.__resourceCollectingHelper.setIsCollectingAvailable(False, friendSwitching=isInFriend)
        else:
            self.__resourceCollectingHelper.setIsCollectingAvailable(True, friendSwitching=isInFriend)

    def __onFriendHangarEnter(self, *args):
        self.__updateFriendHangar(True)
        self.__storePlayerState()
        self.__heroTankController.onVisibilityChanged(False)
        self.__platoonController.onVisibilityChanged(False)

    def __onFriendHangarExit(self, *args):
        self.__updateFriendHangar(False)
        self.__restorePlayerState()
        self.__heroTankController.onVisibilityChanged(True)
        self.__platoonController.onVisibilityChanged(True)
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
        self.onSetHangToyEffectEnabled(False)
        self.__hangToys()
        if self.__callbackDelayer.hasDelayedCallback(self.__updateResources3DScene):
            self.__callbackDelayer.stopCallback(self.__updateResources3DScene)
        self.__updateResources3DScene(isInFriend=isInFriend)
