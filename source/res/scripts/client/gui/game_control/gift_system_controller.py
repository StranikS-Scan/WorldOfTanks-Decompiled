# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/gift_system_controller.py
import logging
import typing
from functools import partial
from collections import deque
from bootcamp.BootCampEvents import g_bootcampEvents
from constants import Configs
from Event import Event, EventManager
from gifts.gifts_common import ClientReqStrategy
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.gift_system.constants import MAX_CACHED_PLAYERS
from gui.gift_system.hubs import createGiftEventHub
from gui.gift_system.hubs.base.hub_core import IGiftEventHub
from gui.gift_system.requesters.history_requester import GiftSystemHistoryRequester
from gui.gift_system.requesters.state_requester import GiftSystemWebStateRequester
from gui.gift_system.requesters.wait_response_requester import GiftSystemWaitResponseRequester
from gui.gift_system.wrappers import skipNoHubsAction
from helpers import dependency
from helpers.server_settings import GiftSystemConfig
from skeletons.gui.game_control import IGiftSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftsHistoryData, GiftsWebState
    from gui.shared import events
    from helpers.server_settings import ServerSettings, GiftEventConfig
_logger = logging.getLogger(__name__)

class GiftSystemController(IGiftSystemController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__em = EventManager()
        self.onEventHubsCreated = Event(self.__em)
        self.onEventHubsDestroyed = Event(self.__em)
        self.__isLobbyInited = False
        self.__serverSettings = None
        self.__giftSystemSettings = None
        self.__requestWaitResponseQueue = deque()
        self.__eventHubs = {}
        self.__historyRequester = GiftSystemHistoryRequester(self.__onHistoryReceived)
        self.__webStateRequester = GiftSystemWebStateRequester(self.__onWebStateReceived)
        self.__waitResponseRequester = GiftSystemWaitResponseRequester(self.__onWaitResponseReceived)
        return

    def init(self):
        super(GiftSystemController, self).init()
        g_bootcampEvents.onBootcampFinished += self.__onBootcampFinished

    def fini(self):
        g_bootcampEvents.onBootcampFinished -= self.__onBootcampFinished
        self.__requestWaitResponseQueue = deque()
        self.__historyRequester.destroy()
        self.__webStateRequester.destroy()
        self.__waitResponseRequester.destroy()
        self.__em.clear()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onGiftSettingsChanged
        self.__destroyEventHubs(set(self.__eventHubs.keys()), onDisconnect=True)
        self.__serverSettings = self.__giftSystemSettings = None
        return

    def onLobbyInited(self, event=None):
        self.__updateLobbyState(isLobbyInited=True)
        self.__onWebStateReadyChanged(strategy=ClientReqStrategy.AUTO)
        self.__onHistoryReadyChanged(self.__itemsCache.items.giftSystem.isHistoryReady)
        self.__updateReadyListening()

    def getEventHub(self, eventID):
        return self.__eventHubs.get(eventID)

    def getSettings(self):
        return self.__giftSystemSettings

    def requestWebState(self, eventID):
        if eventID not in self.__eventHubs:
            return
        self.__onWebStateReadyChanged(strategy=ClientReqStrategy.DEMAND, eventIDs=[eventID])

    def requestWaitResponse(self, reqEventId, spaID, getUpdatedAtAfter=None, getUpdatedAtBefore=None):
        if reqEventId not in self.__eventHubs:
            return
        if not self.__eventHubs[reqEventId].isWebStateReceived():
            self.__requestWaitResponseQueue.append(partial(self.requestWaitResponse, reqEventId, spaID, getUpdatedAtAfter, getUpdatedAtBefore))
            return
        if not self.__waitResponseRequester.isWaitResponseLimitSet():
            limit = self.__eventHubs[reqEventId].getKeeper().getWaitResponseLimit()
            self.__waitResponseRequester.setWaiResponseLimit(limit)
        self.__waitResponseRequester.request(reqEventId, spaID, getUpdatedAtAfter=getUpdatedAtAfter, getUpdatedAtBefore=getUpdatedAtBefore)

    def __onWaitResponseReceived(self, eventID, result):
        if eventID is None:
            return
        elif result is None:
            _logger.warning('onWaitResponseReceived, result is None, request is not Succeed')
            return
        else:
            limit = self.__eventHubs[eventID].getKeeper().getWaitResponseLimit()
            playersWaitingResponseCount = len(self.__eventHubs[eventID].getKeeper().getPlayersWaitingResponse())
            if playersWaitingResponseCount + limit > MAX_CACHED_PLAYERS:
                self.__waitResponseRequester.stop()
            self.__eventHubs[eventID].processWaitResponse(result)
            return

    def __clear(self):
        self.__updateLobbyState(isLobbyInited=False)
        self.__webStateRequester.stop()
        self.__historyRequester.stop()
        self.__waitResponseRequester.stop()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__requestWaitResponseQueue = deque()

    def __onBootcampFinished(self):
        for eventHub in self.__eventHubs.itervalues():
            eventHub.reset()

    def __onGiftSettingsChanged(self, diff):
        if Configs.GIFTS_CONFIG.value in diff:
            self.__updateGiftSettings()

    def __onHistoryReadyChanged(self, isHistoryReady):
        if not isHistoryReady:
            return
        reqEventIDs = set((eID for eID, eHub in self.__eventHubs.iteritems() if eHub.isHistoryRequired()))
        self.__historyRequester.request(reqEventIDs)

    def __onHistoryReceived(self, history):
        for eventID, eventHub in ((eID, eHub) for eID, eHub in self.__eventHubs.iteritems() if eID in history):
            eventHub.processHistory(history[eventID])

        self.__onWebStateReadyChanged(strategy=ClientReqStrategy.AUTO)

    def __onWebStateReadyChanged(self, strategy, eventIDs=None):
        eventIDs = eventIDs or self.__eventHubs.keys()
        reqEventIDs = set((eID for eID in eventIDs if self.__eventHubs[eID].isWebStateRequired(strategy)))
        self.__webStateRequester.request(reqEventIDs)

    def __onWebStateReceived(self, webState):
        for eventID, eventHub in ((eID, eHub) for eID, eHub in self.__eventHubs.iteritems() if eID in webState):
            eventHub.processWebState(webState[eventID])

        while self.__requestWaitResponseQueue:
            function = self.__requestWaitResponseQueue.popleft()
            if not callable(function):
                logging.error('Object is not callable, got %s', function)
                continue
            function()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onGiftSettingsChanged
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onGiftSettingsChanged
        self.__updateGiftSettings()
        return

    @skipNoHubsAction
    def __createEventHubs(self, hubsToCreate, eventsSettings):
        for eventID in hubsToCreate:
            self.__eventHubs[eventID] = createGiftEventHub(eventID, eventsSettings[eventID], self.__isLobbyInited)

        self.onEventHubsCreated(hubsToCreate)

    @skipNoHubsAction
    def __destroyEventHubs(self, hubsToDestroy, onDisconnect=False):
        if not onDisconnect:
            self.onEventHubsDestroyed(hubsToDestroy)
        for eventID in hubsToDestroy:
            self.__eventHubs[eventID].destroy()
            del self.__eventHubs[eventID]

    @skipNoHubsAction
    def __updateEventHubs(self, hubsToUpdate, eventsSettings):
        for eventID in hubsToUpdate:
            self.__eventHubs[eventID].updateSettings(eventsSettings[eventID])

    def __updateEventHubsSettings(self, prevSettings, newSettings):
        prevEvents, newEvents = prevSettings.events, newSettings.events
        prevEventsIDs, newEventsIDs = set(prevEvents.keys()), set(newEvents.keys())
        self.__destroyEventHubs(prevEventsIDs - newEventsIDs)
        self.__updateEventHubs(prevEventsIDs & newEventsIDs, newEvents)
        self.__createEventHubs(newEventsIDs - prevEventsIDs, newEvents)

    def __updateGiftSettings(self):
        prevSettings = self.__giftSystemSettings or GiftSystemConfig()
        self.__giftSystemSettings = self.__serverSettings.giftSystemConfig
        self.__updateEventHubsSettings(prevSettings, self.__giftSystemSettings)

    def __updateLobbyState(self, isLobbyInited=False):
        self.__isLobbyInited = isLobbyInited
        for eventHub in self.__eventHubs.itervalues():
            eventHub.getMessenger().setMessagesAllowed(isLobbyInited)

    def __updateReadyListening(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        if [ eventHub for eventHub in self.__eventHubs.itervalues() if eventHub.isHistoryRequired() ]:
            g_clientUpdateManager.addCallbacks({'cache.giftsData.isReady': self.__onHistoryReadyChanged})
